"""
Enhanced Looker Studio data extractor with specific selectors for paid media metrics
"""
import time
from typing import Dict, List, Any


class LookerStudioExtractor:
    """Extract data from Looker Studio dashboards"""
    
    def __init__(self, page):
        self.page = page
        
    def wait_for_dashboard_load(self, timeout=10):
        """Wait for Looker Studio dashboard to fully load"""
        try:
            # Wait for common Looker Studio elements
            self.page.wait_for_selector('canvas, table, [class*="chart"]', timeout=timeout * 1000)
            time.sleep(3)  # Additional wait for dynamic content
        except Exception as e:
            print(f"Warning: Dashboard load wait timeout: {e}")
    
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
    
    def explore_navigation(self, max_clicks=5) -> List[str]:
        """Click through navigation elements to discover hidden data"""
        explored = []
        
        try:
            # Find navigation elements
            nav_selectors = [
                'button[role="tab"]',
                '[class*="tab"]:not([class*="table"])',
                '[class*="page-selector"]',
                'button[class*="nav"]'
            ]
            
            nav_elements = []
            for selector in nav_selectors:
                elements = self.page.query_selector_all(selector)
                nav_elements.extend(elements)
            
            # Click through visible navigation elements
            for idx, element in enumerate(nav_elements[:max_clicks]):
                try:
                    if element.is_visible():
                        element_text = element.inner_text().strip() or f"Element_{idx}"
                        print(f"Exploring: {element_text}")
                        
                        element.click()
                        time.sleep(2)  # Wait for content to load
                        
                        explored.append(element_text)
                        
                except Exception as e:
                    print(f"Error clicking navigation: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error exploring navigation: {e}")
        
        return explored
    
    def extract_all_data(self, explore_nav=True) -> Dict[str, Any]:
        """Extract all data from the dashboard"""
        print("Starting data extraction...")
        
        # Wait for dashboard to load
        self.wait_for_dashboard_load()
        
        # Extract all data types
        data = {
            'metadata': self.extract_page_metadata(),
            'tables': self.extract_tables(),
            'metrics': self.extract_metrics(),
            'charts': self.extract_charts(),
            'filters': self.extract_filters()
        }
        
        # Explore navigation if requested
        if explore_nav:
            data['navigation_explored'] = self.explore_navigation()
            
            # Re-extract data after navigation
            data['tables'].extend(self.extract_tables())
            data['metrics'].extend(self.extract_metrics())
            data['charts'].extend(self.extract_charts())
            
            # Remove duplicates
            data['tables'] = self._deduplicate_list(data['tables'])
            data['metrics'] = self._deduplicate_list(data['metrics'])
            data['charts'] = self._deduplicate_list(data['charts'])
        
        # Add summary
        data['summary'] = {
            'total_tables': len(data['tables']),
            'total_metrics': len(data['metrics']),
            'total_charts': len(data['charts']),
            'total_filters': len(data['filters'])
        }
        
        print(f"Extraction complete: {data['summary']}")
        
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
