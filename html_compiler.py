import streamlit as st
import re
import tempfile
import webbrowser
import os

class HTMLErrorCorrector:
    def __init__(self):
        self.errors = []
        self.corrected_html = []
        self.tag_stack = []
        self.line_number = 1

    def parse(self, html_content):
        """
        Parse HTML content using regular expressions to find tags,
        report mismatches and missing closing tags, and auto-correct the HTML.
        """
        pos = 0
        # Regex to capture tags. It captures an optional slash for closing tags,
        # the tag name, and any attributes (or self-closing slash) in group 3.
        tag_pattern = re.compile(r'<\s*(/?)(\w+)([^>]*)>')
        
        for match in tag_pattern.finditer(html_content):
            start, end = match.span()
            # Process text data between tags
            data = html_content[pos:start]
            if data:
                self.corrected_html.append(data)
                self.line_number += data.count('\n')
            
            full_tag = match.group(0)
            closing_slash = match.group(1)
            tag_name = match.group(2)
            rest = match.group(3)

            # Check if it's a self-closing tag (e.g. <br/>, <img ... />)
            if not closing_slash:
                if rest.strip().endswith('/'):
                    # Self-closing tag; simply add it.
                    self.corrected_html.append(full_tag)
                else:
                    # Start tag: add it and push onto the stack.
                    self.corrected_html.append(full_tag)
                    self.tag_stack.append((tag_name, self.line_number))
            else:
                # End tag encountered.
                if not self.tag_stack:
                    # No matching opening tag.
                    self.errors.append({
                        'line': self.line_number,
                        'type': 'error',
                        'message': f"Closing tag </{tag_name}> without opening tag"
                    })
                    self.corrected_html.append(full_tag)
                else:
                    last_tag, tag_line = self.tag_stack[-1]
                    if last_tag != tag_name:
                        # Mismatched closing tag.
                        self.errors.append({
                            'line': self.line_number,
                            'type': 'error',
                            'message': f"Mismatched tags: expected </{last_tag}>, got </{tag_name}>"
                        })
                        # Auto-correct: close the last tag properly before adding the current one.
                        self.corrected_html.append(f"</{last_tag}>")
                        self.tag_stack.pop()
                        self.corrected_html.append(full_tag)
                    else:
                        # Correct closing tag.
                        self.corrected_html.append(full_tag)
                        self.tag_stack.pop()
            
            pos = end

        # Process any remaining data after the last tag.
        data = html_content[pos:]
        if data:
            self.corrected_html.append(data)
        
        # Close any unclosed tags.
        while self.tag_stack:
            tag, tag_line = self.tag_stack.pop()
            self.corrected_html.append(f"</{tag}>")
            self.errors.append({
                'line': self.line_number,
                'type': 'error',
                'message': f"Missing closing tag for <{tag}>"
            })
        return "".join(self.corrected_html)

    def get_corrected_html(self):
        return "".join(self.corrected_html)


class HTMLCompiler:
    def __init__(self):
        self.parser = HTMLErrorCorrector()
        
    def compile(self, html_content):
        """Compile HTML content and return corrected version with error report."""
        self.parser = HTMLErrorCorrector()
        corrected = self.parser.parse(html_content)
        return {
            'corrected_html': corrected,
            'errors': self.parser.errors
        }
    
    def validate_html(self, html_content):
        """
        Very basic validation: compile and check if any errors were recorded.
        """
        result = self.compile(html_content)
        return len(result['errors']) == 0
    
    def format_html(self, html_content):
        """
        Format HTML content with simple indentation.
        This splits the HTML into tags and data and indents nested tags.
        """
        tag_pattern = re.compile(r'(<[^>]+>)')
        parts = tag_pattern.split(html_content)
        indent = 0
        formatted_lines = []
        for part in parts:
            if not part.strip():
                continue
            # Check if part is a tag
            if tag_pattern.fullmatch(part):
                # If it's a closing tag, decrease indent
                if re.match(r'<\s*/', part):
                    indent = max(indent - 1, 0)
                formatted_lines.append("    " * indent + part)
                # Increase indent after an opening tag that is not self-closing.
                if re.match(r'<\s*(?!/)(\w+)(?![^>]*\/>)', part):
                    indent += 1
            else:
                # For text content, split by newline if necessary
                for line in part.splitlines():
                    if line.strip():
                        formatted_lines.append("    " * indent + line.strip())
        return "\n".join(formatted_lines)


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
                st.rerun()

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
            st.rerun()

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
