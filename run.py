# MIT License

# Copyright (c) 2025 Mikhael Lerman checkthisresume.com

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import re
import fileinput

parser = argparse.ArgumentParser()
parser.add_argument("--file", help="file to process")
parser.add_argument("--old", help="yes : escaped is preserved creates only YES_CONTAINS_LINUX_CMD.sh.bat and YES_CONTAINS_PSEXEC_CMD.sh.bat (read_only), no : recreate escaped")
args = parser.parse_args()

read_only=False
if args.old == "yes":
    read_only=True

if args.file is not None:
    #print "processing : " + args.file
    fh = open(args.file)
    if not read_only:
        new_fname = args.file.replace(".curlyout", ".escaped")
        fw = open(new_fname, "w")
        #fw = open(args.file + ".escaped", "w")
    contains_linux_cmd=False
    contains_psexec_cmd=False
    for line in fh:
        if not line.rstrip():
            processed_line = "rem\n"
            #processed_line = ""
        else:
            processed_line = line
            line_stripped=line.rstrip()
            line_stripped_both=line_stripped.lstrip()
            if not line_stripped_both.startswith(':') and not line_stripped_both.startswith('w_') and not line_stripped_both.startswith('p_') and not line_stripped_both.startswith('call ') and not line_stripped_both.startswith('kitty') and not line_stripped_both.startswith('rem ') and not line_stripped_both.startswith('goto') and not line_stripped_both.startswith('kittygotoline ') and not line_stripped_both.startswith('{{{') and not line_stripped_both.startswith('}}}'):
                contains_linux_cmd=True
            #if one of the lines start with p_ then there are commands for a remote windows machine
            if line_stripped_both.startswith('p_'):
                contains_psexec_cmd=True
                
            pos_goto=line_stripped.find(" goto ")               
            if pos_goto != -1:
                label_str_1=line_stripped[pos_goto+6:]
                label_str=":" + label_str_1
                #print "==label_str : " + label_str + "== " + str(pos_goto)
                label_line=0
                with open(args.file) as reFile:
                    for num, line2 in enumerate(reFile, 1):
                        if label_str in line2:
                            #print 'found at line:', num 
                            label_line = num
                processed_line = processed_line.replace(" goto "+label_str_1, " kittygotoline " + str(label_line) )
                #print "==processed_line : " + processed_line + "== "
                
            if line_stripped.startswith('w_goto '):
                label = line_stripped.split()[1]
                #print "==label : " + label + "=="
                
                label_line=0
                with open(args.file) as reFile:
                    for num, line2 in enumerate(reFile, 1):
                        if ":"+label in line2:
                            #print 'found at line:', num 
                            label_line = num
                #processed_line = line_stripped + " & rem \n"
                processed_line = "kittygotoline " + str(label_line) + "\n"
                
        # my own escapes, not needed
        #processed_line=processed_line.replace("\\n", "\\_n")
        #processed_line=processed_line.replace("\\t", "\\_t")

        # backslash comme \n, experimental, semble OK pour linux
        # il y a un problem si le string est entre des double quotes comme " ... \n ... " pour linux
        processed_line=processed_line.replace("\\", "\\x5c\\x5c")

        # normal escapes
        processed_line=processed_line.replace('"', "\\x22")		# necessaire pour linux
        processed_line=processed_line.replace("&", "\\x26")
        processed_line=processed_line.replace("(", "\\x28")
        processed_line=processed_line.replace(")", "\\x29")
        # redirects and pipes
        processed_line=processed_line.replace(">", "\\x3e")  # attention a la capitalisation pour le revert de l'escape
        processed_line=processed_line.replace("<", "\\x3c")
        processed_line=processed_line.replace("|", "\\x7c")	
        if not read_only:
            fw.write(processed_line)
    fh.close()
    if not read_only:
        fw.close()
    with open("YES_CONTAINS_LINUX_CMD.sh.bat", "w") as fvar:
        if contains_linux_cmd:
            fvar.write("set YES_CONTAINS_LINUX_CMD=yes")
        else :
            fvar.write("set YES_CONTAINS_LINUX_CMD=no")
    # now for YES_CONTAINS_PSEXEC_CMD
    with open("YES_CONTAINS_PSEXEC_CMD.sh.bat", "w") as fvar:
        if contains_psexec_cmd:
            fvar.write("set YES_CONTAINS_PSEXEC_CMD=yes")
        else :
            fvar.write("set YES_CONTAINS_PSEXEC_CMD=no")
