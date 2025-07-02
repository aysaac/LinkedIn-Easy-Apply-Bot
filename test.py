import markdown

with open(r"/mnt/c/Users/isaac/PycharmProjects/LinkedIn-Easy-Apply-Bot/example.md", "r", encoding="utf-8") as f:
    md_text = f.read()


#%%
import os

# os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")

from weasyprint import HTML
html = markdown.markdown(md_text, extensions=["fenced_code", "codehilite"])
HTML(string=html).write_pdf("output.pdf")
#%%