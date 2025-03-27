import streamlit as st
from bs4 import BeautifulSoup
from html.parser import HTMLParser
import re
import tempfile
import webbrowser
import os

class HTMLErrorCorrector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []
        self.corrected_html = []
        self.current_tag = None
        self.tag_stack = []
        self.line_number = 1
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        self.tag_stack.append(tag)
        self.corrected_html.append(f"<{tag}{self._format_attrs(attrs)}>")
        
    def handle_endtag(self, tag):
        if not self.tag_stack:
            self.errors.append({
                'line': self.line_number,
                'type': 'error',
                'message': f"Closing tag </{tag}> without opening tag"
            })
            return
            
        if self.tag_stack[-1] != tag:
            self.errors.append({
                'line': self.line_number,
                'type': 'error',
                'message': f"Mismatched tags: expected </{self.tag_stack[-1]}>, got </{tag}>"
            })
            # Auto-correct by closing the current tag and opening the correct one
            self.corrected_html.append(f"</{self.tag_stack[-1]}>")
            self.tag_stack.pop()
            self.corrected_html.append(f"<{tag}>")
            self.tag_stack.append(tag)
        else:
            self.corrected_html.append(f"</{tag}>")
            self.tag_stack.pop()
            
    def handle_data(self, data):
        self.corrected_html.append(data)
        self.line_number += data.count('\n')
        
    def handle_entityref(self, name):
        self.corrected_html.append(f"&{name};")
        
    def handle_charref(self, name):
        self.corrected_html.append(f"&#{name};")
        
    def _format_attrs(self, attrs):
        if not attrs:
            return ""
        return " " + " ".join(f'{k}="{v}"' for k, v in attrs)
    
    def get_corrected_html(self):
        # Close any unclosed tags
        while self.tag_stack:
            tag = self.tag_stack.pop()
            self.corrected_html.append(f"</{tag}>")
            self.errors.append({
                'line': self.line_number,
                'type': 'error',
                'message': f"Missing closing tag for <{tag}>"
            })
            
        return "".join(self.corrected_html)

class HTMLCompiler:
    def __init__(self):
        self.parser = HTMLErrorCorrector()
        
    def compile(self, html_content):
        """Compile HTML content and return corrected version with error report"""
        self.parser = HTMLErrorCorrector()
        self.parser.feed(html_content)
        return {
            'corrected_html': self.parser.get_corrected_html(),
            'errors': self.parser.errors
        }
    
    def validate_html(self, html_content):
        """Validate HTML structure and return True if valid"""
        try:
            BeautifulSoup(html_content, 'html5lib')
            return True
        except Exception as e:
            return False
    
    def format_html(self, html_content):
        """Format HTML content with proper indentation"""
        soup = BeautifulSoup(html_content, 'html5lib')
        return soup.prettify()
