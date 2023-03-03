from dnapy import helper
import array
import numpy as np
import argparse
import Bio.SeqIO.QualityIO
import sys

NUCS = ['A', 'C', 'G', 'T']
ILLUMINA_QUAL_OFFSET = 33 #from import tenkit.constants as tk_constants

class barcodeFastqIter:
    def __init__(self,fastqFiles,barcodeDist,start,end,conf=.975):
        self.nMatch = 0
        self.nCorrected = 0
        self.nBad = 0
        self.nTotal = 0
        self.fastqFiles=fastqFiles
        self.start=start
        self.end=end
        self.barcodeDist=barcodeDist
        self.barcode_confidence_threshold=conf
        self.fastqHandles=[helper.openNormalOrGz(x) for x in self.fastqFiles]
        self.reads=[Bio.SeqIO.QualityIO.FastqGeneralIterator(x) for x in self.fastqHandles]
    
    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        helper.closeFiles(self.fastqHandles)

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        for currentReads in zip(*self.reads):
            barcode=currentReads[0][1][(self.start-1):(self.end)]
            barcodeQual=currentReads[0][2][(self.start-1):(self.end)]
            self.nTotal+=1
            if barcode in self.barcodeDist:
                self.nMatch+=1
                return (barcode,barcode,currentReads)
            else:
                corrected = correct_bc_error(self.barcode_confidence_threshold, barcode, barcodeQual, self.barcodeDist)
                if corrected:
                    self.nCorrected+=1
                    return(corrected,barcode,currentReads)
                else:
                    self.nBad+=1
                    return(None,barcode,currentReads)
        raise StopIteration()



#./lib/python/cellranger/stats.py
def correct_bc_error(bc_confidence_threshold, seq, qual, wl_dist):
    '''Attempt to correct an incorrect BC sequence by computing
    the probability that a Hamming distance=1 BC generated
    the observed sequence, accounting for the prior distribution
    of the whitelist barcodes (wl_dist), and the QV of the base
    that must have been incorrect'''

    # QV values
    qvs = np.fromstring(qual, dtype=np.byte) - ILLUMINA_QUAL_OFFSET
    # Char array of read
    a = list(seq)
    # Likelihood of candidates
    wl_cand = []
    likelihoods = []

    # Enumerate Hamming distance 1 sequences - if a sequence
    # is on the whitelist, compute it's likelihood.
    for pos in range(len(a)):
        existing = a[pos]
        for c in NUCS:
            if c == existing:
                continue
            a[pos] = c
            test_str = ''.join(a)
            # prior probability of this BC
            p_bc = wl_dist.get(test_str)
            if p_bc is not None:
                # probability of the base error
                edit_qv = min(33.0, float(qvs[pos]))
                p_edit = 10.0**(-edit_qv / 10.0)
                wl_cand.append(test_str)
                likelihoods.append(p_bc * p_edit)
        a[pos] = existing

    posterior = np.array(likelihoods)
    posterior /= posterior.sum()
    if len(posterior) > 0:
        pmax = posterior.max()
        if pmax > bc_confidence_threshold:
            return wl_cand[np.argmax(posterior)]
    return None

def main(argv=None):
    parser = argparse.ArgumentParser(description="A function to read in a fastq file and use 10x algorithm to correct barcodes based on abundance of barcodes differing by a single base and quality scores")
    parser.add_argument('fastqFile', help='a fastq file (potentially gzipped) containing the sequence reads containing barcodes to be checked',type=helper.checkFile)
    parser.add_argument('-b','--barcodeCounts', help='a headerless csv file giving barcode,count in each row',type=helper.checkFile,required=True)
    parser.add_argument("-s","--start", help="Start position of barcode in reads (1-based)", default=1,type=int)
    parser.add_argument("-e","--end", help="End position of barcode in reads (1-based)", default=16,type=int)
    parser.add_argument("-t","--barcode_confidence_threshold", help='Replace the observed barcode with the whitelist barcode with the highest posterior probability that exceeds this value', default=.975,type=float)
    parser.add_argument("-d","--dots", help="output dot to stderr every X reads. Input a negative number to suppress output (default:-1)", default=-1,type=int)
    args=parser.parse_args(argv)

    barcode_counts={xx[0]:int(xx[1]) for xx in helper.readSimpleCsv(args.barcodeCounts)}
    nBarcodes = sum(barcode_counts.values())
    barcode_dist = {xx:yy/nBarcodes for xx,yy in barcode_counts.items()}

    with barcodeFastqIter([args.fastqFile],barcode_dist,args.start,args.end,args.barcode_confidence_threshold) as fastqIter:
        for corrected,barcode,reads in fastqIter:
            sys.stdout.write('%s,%s,%s\n' % (reads[0][0],barcode,corrected))
            if args.dots>0:
                if (fastqIter.nTotal) % args.dots==0:
                    sys.stderr.write('.')
                    sys.stderr.flush()
    if args.dots>0:
        sys.stderr.write("\nMatching barcodes: "+str(fastqIter.nMatch)+" Corrected barcodes: "+str(fastqIter.nCorrected)+" Bad barcodes: "+str(fastqIter.nBad)+"\n")
 

if __name__ == '__main__':
    main()
