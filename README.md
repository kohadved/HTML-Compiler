# HTML Compiler

A modern HTML compiler and validator that helps you check, correct, and format your HTML code. Built with Python and featuring a user-friendly GUI interface.

## Features

- HTML validation and error detection
- Automatic HTML correction
- Real-time preview in browser
- Modern GUI interface
- Dark/Light theme support
- Full-screen mode
- Error reporting
- Code formatting

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/html-compiler.git
cd html-compiler
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode

To run the application in development mode:
```bash
python gui.py
```

### Building Executable

To create a standalone executable:

1. Make sure you have all requirements installed:
```bash
pip install -r requirements.txt
```

2. Run the build script:
```bash
python build_executable.py
```

3. The executable will be created in the `dist` folder:
   - `dist/HTML Compiler.exe` - The standalone executable
   - `dist/HTML_Compiler.zip` - Distribution package

## Usage

1. Launch the application
2. Enter your HTML code in the input section
3. Click "Compile HTML" to check and correct your code
4. View the corrected HTML in the output section
5. Click "Preview in Browser" to see the result
6. Use "Clear All" to reset all sections

## Features in Detail

### HTML Validation
- Checks for proper HTML structure
- Validates HTML5 compliance
- Detects common HTML errors

### Error Correction
- Fixes mismatched tags
- Closes unclosed tags
- Corrects invalid nesting

### Preview
- Real-time preview in default browser
- Shows how the HTML will render
- Helps identify visual issues

### Interface
- Modern, clean design
- Dark/Light theme support
- Full-screen mode
- Scrollable sections
- Status updates

## Contributing

Contributors:
- Nakul Makode
- Vedant Kohad
- Yogeshwar Tiwari

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the contributors.

## Acknowledgments

- BeautifulSoup4 for HTML parsing
- html5lib for HTML5 validation
- PyInstaller for executable creation 
