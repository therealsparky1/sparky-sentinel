"""
HTML Parser Module
==================
A flexible data extraction engine for parsed HTML using BeautifulSoup4 and lxml.

Schema-driven extraction supporting CSS selectors, XPath, and regex patterns.
"""

import re
from typing import Any, Dict, List, Optional, Union
from bs4 import BeautifulSoup, Tag
from lxml import etree


class HTMLParser:
    """Main HTML parser class with schema-based extraction."""
    
    def __init__(self, html: str, parser: str = "lxml"):
        """
        Initialize parser with HTML content.
        
        Args:
            html: Raw HTML string
            parser: Parser backend ('lxml', 'html.parser', 'html5lib')
        """
        self.html = html
        self.soup = BeautifulSoup(html, parser)
        self.parser = parser
    
    def parse(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data according to schema definition.
        
        Args:
            schema: Dictionary defining extraction rules
            
        Returns:
            Extracted data as dictionary
            
        Schema Format:
        {
            "field_name": {
                "selector": "css selector or xpath",
                "type": "text|link|image|table|html|list",
                "multiple": True|False,
                "regex": "pattern to match",
                "clean": True|False,
                "default": "fallback value",
                "attr": "attribute name for extraction"
            }
        }
        """
        result = {}
        
        for field_name, field_config in schema.items():
            try:
                value = self._extract_field(field_config)
                result[field_name] = value
            except Exception as e:
                # Handle missing elements gracefully
                default = field_config.get("default", None)
                result[field_name] = default
                
        return result
    
    def _extract_field(self, config: Dict[str, Any]) -> Any:
        """Extract a single field based on configuration."""
        selector = config.get("selector", "")
        field_type = config.get("type", "text")
        multiple = config.get("multiple", False)
        regex = config.get("regex")
        clean = config.get("clean", True)
        attr = config.get("attr")
        default = config.get("default", None)
        
        # Find elements
        elements = self._find_elements(selector, config.get("selector_type", "css"))
        
        if not elements:
            return default
        
        # Extract based on type
        if multiple:
            values = []
            for elem in elements:
                val = self._extract_value(elem, field_type, attr, clean, regex)
                if val is not None:
                    values.append(val)
            return values if values else default
        else:
            elem = elements[0] if elements else None
            if elem is None:
                return default
            return self._extract_value(elem, field_type, attr, clean, regex)
    
    def _find_elements(self, selector: str, selector_type: str = "css") -> List[Tag]:
        """Find elements using CSS selector or XPath."""
        if not selector:
            return []
        
        try:
            if selector_type == "xpath":
                # Use lxml for XPath
                dom = etree.HTML(str(self.soup))
                xpath_result = dom.xpath(selector)
                # Convert back to BeautifulSoup tags
                results = []
                for item in xpath_result:
                    if hasattr(item, 'tag'):
                        html_str = etree.tostring(item, encoding='unicode')
                        results.append(BeautifulSoup(html_str, self.parser))
                return results
            else:
                # CSS selector (default)
                return self.soup.select(selector)
        except Exception:
            return []
    
    def _extract_value(self, element: Tag, field_type: str, attr: Optional[str],
                       clean: bool, regex: Optional[str]) -> Any:
        """Extract value from element based on type."""
        if field_type == "text":
            text = element.get_text()
            if clean:
                text = self._clean_text(text)
            if regex:
                match = re.search(regex, text)
                return match.group(1) if match and match.groups() else text
            return text
        
        elif field_type == "html":
            return str(element)
        
        elif field_type == "link":
            href = element.get("href", "")
            return self._clean_text(href) if clean else href
        
        elif field_type == "image":
            src = element.get("src", element.get("data-src", ""))
            alt = element.get("alt", "")
            return {
                "src": self._clean_text(src) if clean else src,
                "alt": self._clean_text(alt) if clean else alt
            }
        
        elif field_type == "table":
            return self._extract_table(element)
        
        elif field_type == "attr":
            if attr:
                val = element.get(attr, "")
                return self._clean_text(val) if clean else val
            return None
        
        return None
    
    def _extract_table(self, table_elem: Tag) -> List[List[str]]:
        """Extract table data as 2D array."""
        rows = []
        for tr in table_elem.find_all("tr"):
            cells = []
            for td in tr.find_all(["td", "th"]):
                cells.append(self._clean_text(td.get_text()))
            if cells:
                rows.append(cells)
        return rows
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not isinstance(text, str):
            return ""
        
        # Decode HTML entities
        text = BeautifulSoup(text, "html.parser").get_text()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text


def parse_html(html: str, schema: Dict[str, Any], parser: str = "lxml") -> Dict[str, Any]:
    """
    Extract data from HTML using a schema definition.
    
    Args:
        html: Raw HTML string
        schema: Dictionary defining extraction rules
        parser: Parser backend (default: 'lxml')
        
    Returns:
        Dictionary with extracted data
        
    Example:
        schema = {
            "title": {
                "selector": "h1.title",
                "type": "text"
            },
            "links": {
                "selector": "a",
                "type": "link",
                "multiple": True
            }
        }
        
        data = parse_html(html_content, schema)
    """
    parser_obj = HTMLParser(html, parser)
    return parser_obj.parse(schema)


# Convenience functions
def extract_text(html: str, selector: str, clean: bool = True) -> Optional[str]:
    """Quick extract text from HTML."""
    schema = {
        "result": {
            "selector": selector,
            "type": "text",
            "clean": clean
        }
    }
    return parse_html(html, schema).get("result")


def extract_links(html: str, selector: str = "a") -> List[str]:
    """Quick extract all links from HTML."""
    schema = {
        "links": {
            "selector": selector,
            "type": "link",
            "multiple": True
        }
    }
    return parse_html(html, schema).get("links", [])


def extract_images(html: str, selector: str = "img") -> List[Dict[str, str]]:
    """Quick extract all images from HTML."""
    schema = {
        "images": {
            "selector": selector,
            "type": "image",
            "multiple": True
        }
    }
    return parse_html(html, schema).get("images", [])
