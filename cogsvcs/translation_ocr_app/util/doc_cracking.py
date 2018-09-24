from tika import parser

def crack_pdf(fp):
    parsed = parser.from_file(fp)
    #print(parsed["metadata"])
    return parsed["content"]

if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("-f","--filepath",help="Filepath")
    args = argparser.parse_args()
    
    crack_pdf(args.filepath)