import argparse
import sys
from dnapy import helper
from dnapy import trie

def main(argv=None):
    parser = argparse.ArgumentParser(description="A function to read in two sets of barcodes and validate that all barcodes in the first set appear in second set or are 1 character from a barcode in the first set. Output one row for each barcode with three columns giving the original barcode, the closest assigned target (or targets separated by semicolon) and the distance to closest target barcode (9999 for unassigned barcodes) to standard out")
    parser.add_argument('barcodes', help='a headerless csv file (potentially gzipped) where the first column contains barcodes to check',type=helper.checkFile)
    parser.add_argument('targetBarcodes', help='a headerless csv file (potentially gzipped) where the first column contains target barcodes to compare to',type=helper.checkFile)
    parser.add_argument("-q","--quiet", help="if set then do not output final counts to standard error",action='store_true')
    args=parser.parse_args(argv)


    barcodes=[ii[0] for ii in helper.readSimpleCsv(args.barcodes)]
    targetTrie=trie.Trie()
    for ii in helper.readSimpleCsv(args.targetBarcodes):targetTrie.insert(ii[0])
    nMatch=0
    nOneOff=0
    nProblem=0
    for ii in barcodes:
        result=targetTrie.checkError(ii)
        if not result:
            nProblem+=1
            best=9999
            targets=''
        else:
            best=min([r[1] for r in result])
            targets=';'.join([r[0] for r in result if r[1]==best])
            if best==0:
                nMatch+=1
            elif best==1:
                nOneOff+=1
            else:
                raise RuntimeError('Unexpected distance in calculating barcode '+ii+' distance. This should not happen')
        sys.stdout.write('%s,%s,%d\n' % (ii,targets,best))

    if not args.quiet:
        sys.stderr.write("Barcodes matching: "+str(nMatch)+" Barcodes one off: "+str(nOneOff)+" Barcodes not matching: "+str(nProblem)+"\n")

            

if __name__ == '__main__':
    main()
