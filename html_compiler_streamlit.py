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

def main():
    st.set_page_config(
        page_title="HTML Compiler",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .stTextArea {
            font-family: 'Consolas', monospace;
        }
        .error-message {
            color: #dc2626;
            background-color: #fee2e2;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .success-message {
            color: #059669;
            background-color: #d1fae5;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .error-count {
            color: #dc2626;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("HTML Compiler")
    st.markdown("Validate, format, and correct your HTML code")

    # Initialize the compiler
    compiler = HTMLCompiler()

    # Default HTML template
    default_html = """<!DOCTYPE html>
<html>
<head>
    <title>Sample HTML</title>
</head>
<body>
    <h1>Welcome to HTML Compiler</h1>
    <p>Start editing your HTML code here!</p>
</body>
</html>"""

    # Initialize session state
    if 'input' not in st.session_state:
        st.session_state.input = default_html
    if 'output' not in st.session_state:
        st.session_state.output = ""
    if 'errors' not in st.session_state:
        st.session_state.errors = []

    # Create two columns for input and output
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input HTML")
        input_html = st.text_area(
            "Enter your HTML code",
            value=st.session_state.input,
            height=400,
            key="input_area"
        )

    with col2:
        st.subheader("Output HTML")
        st.text_area(
            "Compiled HTML",
            value=st.session_state.output,
            height=400,
            key="output_area",
            disabled=True
        )

    # Buttons row
    col3, col4, col5 = st.columns(3)

    with col3:
        if st.button("Compile HTML", type="primary"):
            with st.spinner("Compiling..."):
                result = compiler.compile(input_html)
                st.session_state.output = result['corrected_html']
                st.session_state.input = input_html
                st.session_state.errors = result['errors']
                
                if result['errors']:
                    st.error(f"Found {len(result['errors'])} HTML errors:")
                    for error in result['errors']:
                        st.error(f"Line {error['line']}: {error['message']}")
                else:
                    st.success("HTML compiled successfully!")
                st.experimental_rerun()

    with col4:
        if st.button("Preview in Browser"):
            if st.session_state.output:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
                    f.write(st.session_state.output)
                    temp_path = f.name
                webbrowser.open('file://' + temp_path)
            else:
                st.warning("Please compile HTML first!")

    with col5:
        if st.button("Clear All"):
            st.session_state.input = default_html
            st.session_state.output = ""
            st.session_state.errors = []
            st.experimental_rerun()

    # Display errors in a separate section
    if st.session_state.errors:
        st.markdown("### Error Details")
        for error in st.session_state.errors:
            st.error(f"Line {error['line']}: {error['message']}")

    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ by Nakul Makode, Vedant Kohad, Yogeshwar Tiwari")

if __name__ == "__main__":
    main() 
