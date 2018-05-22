import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help = "The input file to be transfomred", required = True)
    parser.add_argument("-r", "--replacements", help = "The tab delimited replacement file to be used", required = True)
    parser.add_argument("-o", "--output", help = "The location of the output file.  Leave blank to overwrite.")

    args = parser.parse_args()
    with open(args.input, 'r') as inp:
        file_contents = inp.read()
    
    with open(args.replacements, 'r') as rep:
        rep_contents = rep.readlines()
        rep_list = [x.split("\t") for x in rep_contents]
    
    for pat in rep_list:
        print(pat)
        print(len(pat))
        instances = file_contents.count(pat[0])
        print("Found {} instances of {} and replacing it with {}".format(instances, pat[0], pat[1]))
        file_contents = file_contents.replace(pat[0], pat[1])
    
    out_file = args.input
    if args.output is not None:
        out_file = args.output
    
    with open(out_file, 'w') as out:
        print("Outputting to {}".format(out_file))
        out.write(file_contents)
    
