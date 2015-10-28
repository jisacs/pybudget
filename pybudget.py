import application as app
import argparse


if __name__ == '__main__':
   parser = argparse.ArgumentParser(description='Compta python')
   parser.add_argument('--cmd','-c', dest="cmd", type=str, help='cmd = add, list_cvs or list_pic')
   parser.add_argument('--input','-i', dest="input", type=str, help='cvs input file name')
   parser.add_argument('--output','-o', dest="output", type=str, help='cvs output file name')
   parser.add_argument('--db','-d', dest="database", type=str, help='pickle database file name')
   args = parser.parse_args()
   budget_app = app.Application(args)
   budget_app.run()