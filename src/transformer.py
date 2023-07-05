import argparse
import logging
import lxml.etree as ET
import os

data_dir = os.path.join(".", "data")
gen_dir = os.path.join(".", "gen")
out_dir = os.path.join(".", "out")

def get_args():
    parser = argparse.ArgumentParser(
                    prog='graphdb_converter',
                    description='Capture Kanji into a Neo4J db'
                    )
    parser.add_argument('--input-file', dest='infile', default="example.xml")
    parser.add_argument('--output-file', dest='outfile', default="example.html")
    parser.add_argument('--type', dest='type', default="txt")
    # parser.add_argument('--display-txt', dest='display-txt', default=False)
    # parser.add_argument('--run-demo', dest='run-demo', default=False)
    parser.add_argument('--gen-file', dest='genfile', default="example.xslt")

    return parser.parse_args()

def write_text(fn, text):
  with open(fn, "w") as text_file:
    text_file.write(text)

def generate_html(data_fn, xsl_fn, out_fn):
  dom = ET.parse(data_fn)
  xslt = ET.parse(xsl_fn)
  transform = ET.XSLT(xslt)
  newdom = transform(dom)
  html_output_enc = ET.tostring(newdom, pretty_print=True)
  html_output = html_output_enc.decode("utf-8")

  write_text(out_fn, html_output)

  return html_output

def generate_txt(data_fn, xsl_fn, out_fn):
  dom = ET.parse(data_fn)
  xslt = ET.parse(xsl_fn)
  transform = ET.XSLT(xslt)
  txt_output = str(transform(dom))

  write_text(out_fn, txt_output)

  return txt_output

def demo():

  data_fn = os.path.join(data_dir, "kanjidic2.xml")

  xsl_fn = os.path.join(gen_dir, "kanjidic.xslt")
  out_fn = os.path.join(out_dir, "kanjidic2.html")
  # out = generate_html(data_fn, xsl_fn, out_fn)

  data_fn = os.path.join(data_dir, "example.xml")

  xsl_fn = os.path.join(gen_dir, "example.xslt")
  out_fn = os.path.join(out_dir, "output.html")
  out = generate_html(data_fn, xsl_fn, out_fn)
  # print(out)

  xsl_fn = os.path.join(gen_dir, "text_gen.xslt")
  out_fn = os.path.join(out_dir, "output.txt")
  out = generate_txt(data_fn, xsl_fn, out_fn)
  print(out)

def main():
  args = get_args()

  data_fn = os.path.join(data_dir, args.infile)

  xsl_fn = os.path.join(gen_dir, args.genfile)
  out_fn = os.path.join(out_dir, args.outfile)

  out = ""
  if args.type == "txt":
    out = generate_txt(data_fn, xsl_fn, out_fn)
  elif args.type == "html":
    out = generate_html(data_fn, xsl_fn, out_fn)
  else:
    logging.error(f"Given type {args.type} is not supported")

  DISPLAY_TEXT=False
  if DISPLAY_TEXT:
    print(out)

if __name__ == "__main__":
  main()
