"""
Enhanced Looker Studio data extractor with specific selectors for paid media metrics
"""
import time
import os
import tempfile
from typing import Dict, List, Any
from PIL import Image
import pytesseract


class LookerStudioExtractor:
    """Extract data from Looker Studio dashboards"""
    
    def __init__(self, page):
        self.page = page
        
    def wait_for_dashboard_load(self, timeout=30):
        """Wait for Looker Studio dashboard to fully load"""
        try:
            # Wait for common Looker Studio elements with longer timeout
            self.page.wait_for_selector('canvas, table, [class*="chart"]', timeout=timeout * 1000)
            print("     Dashboard elements detected, waiting for full render...")
            time.sleep(25)  # Wait 25 seconds for dynamic content to fully render
        except Exception as e:
            print(f"Warning: Dashboard load wait timeout: {e}")
            print("     Continuing with extraction anyway...")
            # Still continue even if timeout - might have loaded partially
            time.sleep(25)  # Still wait even if selector not found

    def quick_scroll(self, max_scrolls=10):
        """Visible chunked scrolling - scrolls the actual scrollable container"""
        try:
            import time

            print("     🔽 Finding scrollable container...")

            # Find the scrollable container (Looker uses .mainBlock)
            container_info = self.page.evaluate("""
                () => {
                    // Try to find scrollable container
                    const selectors = ['.mainBlock', '[class*="mainBlock"]', '[class*="report-content"]', 'main'];
                    let scrollContainer = null;

                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el && el.scrollHeight > el.clientHeight) {
                            scrollContainer = selector;
                            break;
                        }
                    }

                    // If no container found, fall back to window
                    if (!scrollContainer) {
                        return {
                            found: false,
                            selector: 'window',
                            totalHeight: document.body.scrollHeight,
                            viewportHeight: window.innerHeight
                        };
                    }

                    const container = document.querySelector(scrollContainer);
                    return {
                        found: true,
                        selector: scrollContainer,
                        totalHeight: container.scrollHeight,
                        viewportHeight: container.clientHeight
                    };
                }
            """)

            total_height = container_info['totalHeight']
            viewport_height = container_info['viewportHeight']
            selector = container_info['selector']

            print(f"     Found: {selector}")
            print(f"     Total height: {total_height}px, Visible: {viewport_height}px")

            # Flash background to show scrolling is starting
            self.page.evaluate("""
                document.body.style.backgroundColor = '#ffffcc';
                setTimeout(() => { document.body.style.backgroundColor = ''; }, 500);
            """)
            time.sleep(0.5)

            # Scroll in visible chunks (8 steps down for thoroughness)
            scroll_steps = 8
            for step in range(1, scroll_steps + 1):
                scroll_to = int(total_height * (step / scroll_steps))

                # Scroll the container (not window)
                if container_info['found']:
                    self.page.evaluate(f"""
                        const container = document.querySelector('{selector}');
                        if (container) container.scrollTop = {scroll_to};
                    """)
                else:
                    self.page.evaluate(f"window.scrollTo(0, {scroll_to})")

                # Get actual scroll position
                if container_info['found']:
                    current_pos = self.page.evaluate(f"""
                        const container = document.querySelector('{selector}');
                        return container ? container.scrollTop : 0;
                    """)
                else:
                    current_pos = self.page.evaluate("window.scrollY")

                print(f"     📍 Step {step}/{scroll_steps}: Scrolled to {current_pos}px")
                time.sleep(2.5)  # Increased from 1.5s to 2.5s for lazy loading

            # Final scroll to absolute bottom with verification
            print("     📍 Scrolling to absolute bottom...")
            if container_info['found']:
                self.page.evaluate(f"""
                    const container = document.querySelector('{selector}');
                    if (container) container.scrollTop = container.scrollHeight;
                """)
            else:
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)  # Increased wait for lazy content

            # Repeat scroll to bottom until position stops changing (smart detection)
            print("     📍 Ensuring we reach absolute bottom (smart detection)...")
            last_scroll_pos = -1
            attempts = 0
            max_attempts = 10

            while attempts < max_attempts:
                # Get current scroll position and height
                if container_info['found']:
                    scroll_info = self.page.evaluate(f"""
                        const container = document.querySelector('{selector}');
                        if (container) {{
                            return {{
                                scrollTop: container.scrollTop,
                                scrollHeight: container.scrollHeight,
                                clientHeight: container.clientHeight
                            }};
                        }}
                        return null;
                    """)
                else:
                    scroll_info = self.page.evaluate("""
                        () => ({
                            scrollTop: window.scrollY,
                            scrollHeight: document.body.scrollHeight,
                            clientHeight: window.innerHeight
                        })
                    """)

                if not scroll_info:
                    break

                current_pos = scroll_info['scrollTop']
                max_scroll = scroll_info['scrollHeight'] - scroll_info['clientHeight']

                # Check if we've reached the bottom and position hasn't changed
                if current_pos >= max_scroll - 10 and current_pos == last_scroll_pos:
                    print(f"     ✅ Reached bottom! Position: {current_pos}px / {max_scroll}px")
                    break

                # Scroll to bottom again
                if container_info['found']:
                    self.page.evaluate(f"""
                        const container = document.querySelector('{selector}');
                        if (container) container.scrollTop = container.scrollHeight;
                    """)
                else:
                    self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                print(f"     🔽 Attempt {attempts + 1}: Position {current_pos}px / {max_scroll}px")
                last_scroll_pos = current_pos
                attempts += 1
                time.sleep(2)  # Wait for lazy content to load

            # Get final position
            if container_info['found']:
                final_pos = self.page.evaluate(f"""
                    const container = document.querySelector('{selector}');
                    return container ? container.scrollTop : 0;
                """)
            else:
                final_pos = self.page.evaluate("window.scrollY")

            print(f"     ✅ Final scroll position: {final_pos}px")

            # Scroll back to top (faster - less critical)
            print("     📍 Scrolling back to top...")
            if container_info['found']:
                self.page.evaluate(f"""
                    const container = document.querySelector('{selector}');
                    if (container) container.scrollTop = 0;
                """)
            else:
                self.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)

            print("     ✅ Scroll complete!")

        except Exception as e:
            print(f"     ⚠️  Scroll error (non-critical): {e}")
            pass  # Fail silently - scrolling is optional

    def scroll_page_fully(self):
        """Scroll through entire page to load lazy-loaded content and ensure all data is visible"""
        try:
            print("     🔽 Scrolling page to load all content...")

            # Find the scrollable container - Looker Studio uses specific elements
            # Try to find the main content container
            scrollable_container = None
            container_selectors = [
                '[class*="lego-report-body"]',      # Looker Studio main report
                '[class*="report-content"]',
                '[class*="canvas-container"]',
                'main',
                '#app',
                'body'
            ]

            for selector in container_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        scrollable_container = selector
                        print(f"     Found scrollable container: {selector}")
                        break
                except:
                    continue

            if not scrollable_container:
                scrollable_container = 'body'
                print(f"     Using default: body")

            # Enable smooth scrolling for visibility
            self.page.evaluate("""
                document.documentElement.style.scrollBehavior = 'smooth';
            """)

            # Get initial scroll height
            last_height = self.page.evaluate(f"""
                (() => {{
                    const el = document.querySelector('{scrollable_container}');
                    return el ? el.scrollHeight : document.body.scrollHeight;
                }})()
            """)
            print(f"     Initial scroll height: {last_height}px")

            # Scroll in steps to trigger lazy loading - SLOW AND VISIBLE
            scroll_steps = 10  # More steps for better visibility
            for step in range(1, scroll_steps + 1):
                scroll_position = int(last_height * (step / scroll_steps))
                print(f"     Scrolling to position {scroll_position}px ({step}/{scroll_steps})...")

                # Scroll both window AND container for maximum visibility
                self.page.evaluate(f"""
                    (() => {{
                        // Scroll the window
                        window.scrollTo({{
                            top: {scroll_position},
                            behavior: 'smooth'
                        }});

                        // Also scroll the container if it exists
                        const container = document.querySelector('{scrollable_container}');
                        if (container && container !== document.body) {{
                            container.scrollTop = {scroll_position};
                        }}
                    }})();
                """)
                time.sleep(2)  # Longer wait to make scrolling visible

            # Final scroll to absolute bottom
            print(f"     Scrolling to absolute bottom...")
            self.page.evaluate(f"""
                (() => {{
                    const container = document.querySelector('{scrollable_container}');
                    const maxScroll = container ? container.scrollHeight : document.body.scrollHeight;

                    window.scrollTo({{
                        top: maxScroll,
                        behavior: 'smooth'
                    }});

                    if (container && container !== document.body) {{
                        container.scrollTop = maxScroll;
                    }}
                }})();
            """)
            time.sleep(3)

            # Check if new content loaded (page grew)
            new_height = self.page.evaluate(f"""
                (() => {{
                    const el = document.querySelector('{scrollable_container}');
                    return el ? el.scrollHeight : document.body.scrollHeight;
                }})()
            """)
            if new_height > last_height:
                print(f"     ✓ Page expanded from {last_height}px to {new_height}px - NEW CONTENT LOADED!")
                time.sleep(2)  # Extra wait for new content to render
            else:
                print(f"     Page height unchanged: {new_height}px")

            # Scroll back to top for screenshot consistency
            print(f"     Scrolling back to top...")
            self.page.evaluate(f"""
                (() => {{
                    window.scrollTo({{
                        top: 0,
                        behavior: 'smooth'
                    }});

                    const container = document.querySelector('{scrollable_container}');
                    if (container && container !== document.body) {{
                        container.scrollTop = 0;
                    }}
                }})();
            """)
            time.sleep(2)

            print("     ✅ Full page scroll complete")

        except Exception as e:
            print(f"     ⚠️ Warning: Scroll failed: {e}")
    
    def extract_tables(self) -> List[Dict[str, Any]]:
        """Extract all table data from the dashboard"""
        tables = []
        
        try:
            table_elements = self.page.query_selector_all('table')
            
            for idx, table in enumerate(table_elements):
                try:
                    # Extract headers
                    headers = []
                    header_cells = table.query_selector_all('thead th, thead td')
                    if header_cells:
                        headers = [cell.inner_text().strip() for cell in header_cells]
                    
                    # Extract rows
                    rows = []
                    row_elements = table.query_selector_all('tbody tr, tr')
                    
                    for row in row_elements:
                        cells = row.query_selector_all('td, th')
                        row_data = [cell.inner_text().strip() for cell in cells]
                        
                        if row_data and row_data != headers:  # Avoid duplicate headers
                            rows.append(row_data)
                    
                    if rows:
                        table_data = {
                            'table_id': f'table_{idx + 1}',
                            'headers': headers if headers else None,
                            'rows': rows,
                            'row_count': len(rows),
                            'column_count': len(rows[0]) if rows else 0
                        }
                        tables.append(table_data)
                        
                except Exception as e:
                    print(f"Error extracting table {idx}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error finding tables: {e}")
        
        return tables
    
    def extract_metrics(self) -> List[Dict[str, Any]]:
        """Extract metric cards and KPIs"""
        metrics = []
        
        # Common Looker Studio metric selectors
        metric_selectors = [
            '[class*="scorecard"]',
            '[class*="metric"]',
            '[class*="kpi"]',
            '[data-test-id*="scorecard"]',
            'div[class*="compact-number"]',
            'div[class*="metric-value"]'
        ]
        
        seen_values = set()
        
        for selector in metric_selectors:
            try:
                elements = self.page.query_selector_all(selector)
                
                for element in elements:
                    try:
                        text = element.inner_text().strip()
                        
                        # Skip empty or duplicate values
                        if not text or text in seen_values:
                            continue
                        
                        seen_values.add(text)
                        
                        # Try to parse metric name and value
                        lines = text.split('\n')
                        if len(lines) >= 2:
                            metrics.append({
                                'metric_name': lines[0],
                                'metric_value': lines[1],
                                'full_text': text
                            })
                        else:
                            metrics.append({
                                'metric_value': text,
                                'full_text': text
                            })
                            
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        return metrics
    
    def extract_charts(self) -> List[Dict[str, Any]]:
        """Extract chart information and associated data"""
        charts = []
        
        try:
            # Find all chart containers
            chart_selectors = [
                'canvas',
                'svg[class*="chart"]',
                'div[class*="chart-container"]',
                'div[class*="visualization"]'
            ]
            
            for selector in chart_selectors:
                elements = self.page.query_selector_all(selector)
                
                for idx, element in enumerate(elements):
                    try:
                        chart_data = {
                            'chart_id': f'chart_{len(charts) + 1}',
                            'type': element.evaluate('el => el.tagName')
                        }
                        
                        # Try to get chart title from parent or nearby elements
                        try:
                            parent = element.evaluate('el => el.closest("div[class*=\'widget\'], div[class*=\'container\']")')
                            if parent:
                                title_element = self.page.evaluate(
                                    '(el) => el.querySelector("[class*=\'title\'], h1, h2, h3, h4")',
                                    parent
                                )
                                if title_element:
                                    chart_data['title'] = self.page.evaluate('el => el.innerText', title_element).strip()
                        except:
                            pass
                        
                        # For SVG charts, try to extract text labels
                        if element.evaluate('el => el.tagName') == 'svg':
                            try:
                                labels = element.query_selector_all('text')
                                label_texts = [label.inner_text().strip() for label in labels if label.inner_text().strip()]
                                if label_texts:
                                    chart_data['labels'] = label_texts
                            except:
                                pass
                        
                        charts.append(chart_data)
                        
                    except Exception as e:
                        print(f"Error extracting chart: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error finding charts: {e}")
        
        return charts
    
    def extract_text_via_ocr(self) -> Dict[str, Any]:
        """Extract text from dashboard using OCR on screenshots"""
        ocr_data = {
            'extracted_text': '',
            'method': 'OCR (Tesseract)'
        }

        try:
            print("     Running OCR on dashboard screenshot...")

            # Scroll to top first to ensure we start from the beginning
            self.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)

            # Take a screenshot of the entire visible page
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                screenshot_path = tmp_file.name

            # Screenshot the full page (not just viewport)
            self.page.screenshot(path=screenshot_path, full_page=True)
            print(f"     Screenshot saved to: {screenshot_path}")

            # Run OCR on the screenshot
            image = Image.open(screenshot_path)
            print(f"     Image size: {image.size[0]}x{image.size[1]} pixels")

            # Use pytesseract to extract text
            # Using enhanced config for better accuracy on dashboard data
            # --oem 3: Use default OCR Engine Mode (LSTM)
            # --psm 6: Assume a single uniform block of text
            custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
            text = pytesseract.image_to_string(image, config=custom_config)

            # Clean up screenshot
            os.unlink(screenshot_path)

            if text.strip():
                ocr_data['extracted_text'] = text.strip()
                ocr_data['character_count'] = len(text)
                # Count lines with content
                lines_with_content = [line for line in text.split('\n') if line.strip()]
                ocr_data['lines_extracted'] = len(lines_with_content)
                print(f"     ✓ OCR extracted {len(text)} characters from {len(lines_with_content)} lines")
            else:
                print(f"     ⚠️ OCR found no text")

        except Exception as e:
            print(f"     ⚠️ OCR extraction failed: {e}")
            import traceback
            traceback.print_exc()
            ocr_data['error'] = str(e)

        return ocr_data

    def extract_filters(self) -> List[Dict[str, Any]]:
        """Extract active filters and their values"""
        filters = []
        
        try:
            filter_selectors = [
                '[class*="filter"]',
                '[class*="control"]',
                'select',
                'input[type="date"]'
            ]
            
            for selector in filter_selectors:
                elements = self.page.query_selector_all(selector)
                
                for element in elements:
                    try:
                        if element.is_visible():
                            filter_data = {}
                            
                            # Get filter label
                            label = element.evaluate('el => el.getAttribute("aria-label") || el.getAttribute("placeholder") || el.getAttribute("name")')
                            if label:
                                filter_data['name'] = label
                            
                            # Get filter value
                            value = element.evaluate('el => el.value || el.innerText')
                            if value:
                                filter_data['value'] = value.strip()
                            
                            if filter_data:
                                filters.append(filter_data)
                                
                    except:
                        continue
                        
        except Exception as e:
            print(f"Error extracting filters: {e}")
        
        return filters
    
    def extract_page_metadata(self) -> Dict[str, Any]:
        """Extract dashboard metadata"""
        metadata = {
            'title': self.page.title(),
            'url': self.page.url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Try to get dashboard title from page
        try:
            title_selectors = [
                'h1',
                '[class*="dashboard-title"]',
                '[class*="report-title"]'
            ]
            
            for selector in title_selectors:
                element = self.page.query_selector(selector)
                if element:
                    title_text = element.inner_text().strip()
                    if title_text:
                        metadata['dashboard_title'] = title_text
                        break
        except:
            pass
        
        return metadata
    
    def explore_navigation(self, max_clicks=20, enable_ocr=False) -> List[str]:
        """Click through navigation elements to discover hidden data

        Args:
            max_clicks: Maximum number of navigation elements to click
            enable_ocr: Whether to run OCR on each tab
        """
        explored = []
        ocr_results = []  # Store OCR from each tab

        try:
            print("🔍 Searching for navigation tabs...")

            # Enhanced selectors for Looker Studio navigation, including left panels
            # Focus on finding numbered page navigation items
            nav_selectors = [
                # Page navigation - numbered items in sidebar
                '[class*="canvas-page"]',                # Looker Studio page items
                '[class*="page-navigation"]',            # Page navigation containers
                '[class*="page-list"] *',                # Items in page lists
                '[class*="page-item"]',                  # Individual page items
                'nav a',                                 # Links in nav elements
                'nav button',                            # Buttons in nav elements
                'nav div[role="button"]',                # Div buttons in nav
                # Standard tab roles
                'button[role="tab"]',                    # Standard ARIA tabs
                '[role="tab"]',                          # Any element with tab role
                'li[role="tab"]',                        # List items as tabs
                # Generic navigation elements
                '[class*="sidebar"] a',                  # Sidebar links
                '[class*="sidebar"] button',             # Sidebar buttons
                '[class*="sidebar"] [role="button"]',    # Sidebar clickable divs
                '[class*="navigation"] button',          # Buttons in navigation containers
                '[class*="nav-item"]',                   # Navigation items
                '[class*="menu-item"]',                  # Menu items
            ]

            nav_elements = []
            seen_texts = set()  # Track to avoid clicking duplicates

            for selector in nav_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    for element in elements:
                        try:
                            if element.is_visible():
                                text = element.inner_text().strip()
                                # Only add if we haven't seen this text before
                                if text and text not in seen_texts:
                                    nav_elements.append((element, text))
                                    seen_texts.add(text)
                        except:
                            continue
                except Exception as e:
                    print(f"     Warning with selector '{selector}': {e}")
                    continue

            # Additional strategy: find clickable elements with single-digit or short text on the left side
            # These are likely page numbers in Looker Studio's left navigation
            try:
                print("     Searching for numbered page elements...")
                potential_pages = self.page.evaluate("""() => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    return elements
                        .filter(el => {
                            const rect = el.getBoundingClientRect();
                            const text = el.innerText?.trim();
                            // Left side of screen (x < 100), small width, reasonable height, short text
                            return rect.left < 100 &&
                                   rect.width < 100 &&
                                   rect.height > 15 &&
                                   rect.height < 80 &&
                                   text &&
                                   text.length < 20 &&
                                   !text.includes('keyboard'); // Exclude keyboard icons
                        })
                        .map((el, index) => ({
                            index: index,
                            text: el.innerText?.trim(),
                            tagName: el.tagName,
                            className: el.className
                        }));
                }""")

                if potential_pages:
                    print(f"     Found {len(potential_pages)} potential page elements on left side")
                    # Try to get these elements and add them to nav_elements
                    for page_info in potential_pages:
                        text = page_info['text']
                        if text and text not in seen_texts and len(text) < 20:
                            # Find element by its text content
                            try:
                                element = self.page.locator(f'text="{text}"').first
                                if element.is_visible():
                                    nav_elements.append((element, text))
                                    seen_texts.add(text)
                            except:
                                pass
            except Exception as e:
                print(f"     Warning finding numbered pages: {e}")

            print(f"     Found {len(nav_elements)} unique navigation elements")

            # Click through visible navigation elements
            for idx, (element, element_text) in enumerate(nav_elements[:max_clicks]):
                try:
                    if element.is_visible() and element.is_enabled():
                        print(f"     📑 Clicking tab {idx + 1}/{min(len(nav_elements), max_clicks)}: '{element_text}'")

                        # Scroll element into view before clicking
                        element.scroll_into_view_if_needed()
                        time.sleep(0.5)

                        # Click the element
                        element.click()

                        # Wait for dashboard content to fully load after tab change
                        print(f"        Waiting for content to load...")
                        time.sleep(8)  # Wait 8 seconds for data to render and animations to complete

                        # Multiple scrolls to load ALL lazy content on this tab
                        self.quick_scroll()

                        explored.append(element_text)
                        print(f"        ✓ Loaded '{element_text}'")

                        # Run OCR on this tab if enabled
                        if enable_ocr:
                            try:
                                print(f"        📸 Running OCR on '{element_text}'...")
                                ocr_result = self.extract_text_via_ocr()
                                if ocr_result.get('extracted_text'):
                                    ocr_results.append({
                                        'source': f'tab_{element_text}',
                                        'text': ocr_result['extracted_text'],
                                        'char_count': ocr_result.get('character_count', 0)
                                    })
                                    print(f"        ✓ OCR: {ocr_result.get('character_count', 0)} chars from '{element_text}'")
                            except Exception as ocr_error:
                                print(f"        ⚠️ OCR failed for '{element_text}': {ocr_error}")

                except Exception as e:
                    print(f"        ⚠️ Error clicking '{element_text}': {e}")
                    continue

            print(f"✓ Explored {len(explored)} tabs/pages")
            if enable_ocr and ocr_results:
                total_ocr_chars = sum(r.get('char_count', 0) for r in ocr_results)
                print(f"✓ OCR extracted {total_ocr_chars} characters from {len(ocr_results)} tabs")

        except Exception as e:
            print(f"Error exploring navigation: {e}")

        return explored, ocr_results if enable_ocr else (explored, [])
    
    def extract_all_data(self, explore_nav=True, enable_scrolling=False, enable_ocr=False) -> Dict[str, Any]:
        """Extract all data from the dashboard

        Args:
            explore_nav: Whether to click through navigation tabs (default: True)
            enable_scrolling: Whether to scroll pages to load lazy content (default: False)
            enable_ocr: Whether to run OCR on screenshots (default: False)
        """
        print("Starting data extraction...")

        # Wait for dashboard to load
        self.wait_for_dashboard_load()

        # Quick scroll to load lazy content (always enabled, silent)
        self.quick_scroll()

        # Extract all data types from initial view
        print("📊 Extracting from initial view...")
        data = {
            'metadata': self.extract_page_metadata(),
            'tables': self.extract_tables(),
            'metrics': self.extract_metrics(),
            'charts': self.extract_charts(),
            'filters': self.extract_filters(),
            'ocr_text': []  # Store OCR text from each page
        }

        # Run OCR on initial view (OPTIONAL - disabled by default)
        ocr_chars = 0
        if enable_ocr:
            try:
                ocr_result = self.extract_text_via_ocr()
                if ocr_result.get('extracted_text'):
                    data['ocr_text'].append({
                        'source': 'initial_view',
                        'text': ocr_result['extracted_text'],
                        'char_count': ocr_result.get('character_count', 0)
                    })
                    ocr_chars = ocr_result.get('character_count', 0)
            except Exception as ocr_error:
                print(f"     Warning: OCR failed on initial view: {ocr_error}")
                print("     Continuing without OCR...")

        initial_count = {
            'tables': len(data['tables']),
            'metrics': len(data['metrics']),
            'charts': len(data['charts']),
            'ocr_chars': ocr_chars
        }
        print(f"   Initial: {initial_count['tables']} tables, {initial_count['metrics']} metrics, {initial_count['charts']} charts, {initial_count['ocr_chars']} chars via OCR")

        # Explore navigation if requested
        if explore_nav:
            print("\n🗂️  Exploring navigation tabs...")
            navigation_result = self.explore_navigation(enable_ocr=enable_ocr)

            # Handle both old and new return formats
            if enable_ocr and isinstance(navigation_result, tuple):
                data['navigation_explored'], tab_ocr_results = navigation_result
                # Add OCR results from each tab
                if tab_ocr_results:
                    data['ocr_text'].extend(tab_ocr_results)
                    total_tab_ocr = sum(r.get('char_count', 0) for r in tab_ocr_results)
                    print(f"   Total OCR from tabs: {total_tab_ocr} characters from {len(tab_ocr_results)} tabs")
            else:
                data['navigation_explored'] = navigation_result if not isinstance(navigation_result, tuple) else navigation_result[0]

            if data['navigation_explored']:
                print(f"\n📊 Re-extracting data after exploring {len(data['navigation_explored'])} tabs...")

                # Re-extract data after navigation
                new_tables = self.extract_tables()
                new_metrics = self.extract_metrics()
                new_charts = self.extract_charts()

                print(f"   Found: {len(new_tables)} tables, {len(new_metrics)} metrics, {len(new_charts)} charts")

                # Add new data
                data['tables'].extend(new_tables)
                data['metrics'].extend(new_metrics)
                data['charts'].extend(new_charts)

                # Remove duplicates
                print("   Removing duplicates...")
                data['tables'] = self._deduplicate_list(data['tables'])
                data['metrics'] = self._deduplicate_list(data['metrics'])
                data['charts'] = self._deduplicate_list(data['charts'])

                final_count = {
                    'tables': len(data['tables']),
                    'metrics': len(data['metrics']),
                    'charts': len(data['charts'])
                }

                added = {
                    'tables': final_count['tables'] - initial_count['tables'],
                    'metrics': final_count['metrics'] - initial_count['metrics'],
                    'charts': final_count['charts'] - initial_count['charts']
                }

                print(f"   Added from tabs: +{added['tables']} tables, +{added['metrics']} metrics, +{added['charts']} charts")
            else:
                print("   No navigation tabs found to explore")

        # Add summary
        total_ocr_chars = sum(item.get('char_count', 0) for item in data.get('ocr_text', []))
        data['summary'] = {
            'total_tables': len(data['tables']),
            'total_metrics': len(data['metrics']),
            'total_charts': len(data['charts']),
            'total_filters': len(data['filters']),
            'total_ocr_extractions': len(data.get('ocr_text', [])),
            'total_ocr_characters': total_ocr_chars
        }

        print(f"\n✓ Extraction complete: {data['summary']}")

        return data
    
    @staticmethod
    def _deduplicate_list(items: List[Dict]) -> List[Dict]:
        """Remove duplicate dictionaries from list"""
        seen = set()
        unique = []
        
        for item in items:
            item_str = str(sorted(item.items()))
            if item_str not in seen:
                seen.add(item_str)
                unique.append(item)
        
        return unique
