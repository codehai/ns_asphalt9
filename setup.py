from setuptools import setup

setup(
    name="ns_asphalt9",
    include_package_data=True,
    long_description_content_type="text/markdown",
    install_requires=[
        "beautifulsoup4==4.11.2",
        "customtkinter==5.2.0",
        "nxbt==0.1.4",
        "Pillow==9.5.0",
        "pytesseract==0.3.10",
        "Requests==2.31.0",
    ],
    extra_require={"dev": ["pytest"]},
)
