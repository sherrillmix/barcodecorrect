from dnapy import helper
import array
import numpy as np
import argparse
import Bio.SeqIO.QualityIO
import sys
class barcodeIter:
    def __init__(self,correctedBarcodeFile):
        self.correctedBarcodeFile=correctedBarcodeFile
        self.rawCsv= helper.openNormalOrGz(correctedBarcodeFile)
    def __enter__(self):
        return self
    def __exit__(self,exc_type,exc_value,traceback):
        helper.closeFiles(self.rawCsv)
    def __iter__(self):
        return self
    def next(self):
        return self.__next__()
    def __next__(self):
        for currentBar in self.rawCsv:
            name,old,correct=currentBar.strip().split(',')
            return([name,old,correct])
        raise StopIteration()

def commaSep(string):
    out=string.split(',')
    return(out)

class barcodeFastqIter:
    def __init__(self,fastqFiles,correctedBarcodeFile,barcodeSampleDict):
        self.nAssigned = 0
        self.nUnassigned = 0
        self.nBadBarcode = 0
        self.fastqFiles=fastqFiles
        self.fastqHandles=[helper.openNormalOrGz(x) for x in self.fastqFiles]
        self.correctedBarcodeFile=correctedBarcodeFile
        self.correctedBarcodes=barcodeIter(correctedBarcodeFile)
        self.barcodeSampleDict=barcodeSampleDict
        self.reads=[Bio.SeqIO.QualityIO.FastqGeneralIterator(x) for x in self.fastqHandles]
        self.assignCounts={x:0 for x in self.barcodeSampleDict}
    def __enter__(self):
        return self
    def __exit__(self,exc_type,exc_value,traceback):
        helper.closeFiles(self.fastqHandles)
    def __iter__(self):
        return self
    def next(self):
        return self.__next__()
    def __next__(self):
        for currentReadsBarcode in zip(*self.reads,self.correctedBarcodes):
            name,old,correct=currentReadsBarcode[-1]
            currentReads=currentReadsBarcode[:-1]
            if correct is None or correct=='None':
                self.nBadBarcode+=1
            else: 
                if correct in self.barcodeSampleDict:
                    baseName=name.split(' ')[0]
                    if any([xx[0].split(' ')[0]!=baseName for xx in currentReads]): #necessary?
                        raise KeyError("Names desynchronized between files and barcode assignments")
                    self.nAssigned+=1
                    self.assignCounts[correct]+=1
                    #add corrected barcode to read name?
                    return (currentReads,self.barcodeSampleDict[correct],correct)
                else:
                    self.nUnassigned+=1
        raise StopIteration()

def main(argv=None):
    parser = argparse.ArgumentParser(description="A function to read in correct barcodes, barcode to sample assignments and split fastq file(s) into appropriate files")
    parser.add_argument('fastqFiles', help='a fastq file(s) (potentially gzipped) containing the sequence reads to be split. All fastq files must have the reads in the same order',type=helper.checkFile ,nargs='+')
    parser.add_argument('-c','--barcodeCorrections', help='a headerless csv file giving read name,original barcode,corrected barcode in each row i.e. the output of barcodecorrect',type=helper.checkFile,required=True)
    parser.add_argument('-b','--barcodeAssignments', help='a headerless csv file giving barcode,sample assignment in each row',type=helper.checkFile,required=True)
    parser.add_argument('-o','--outputPath', help='a string giving the desired output directory',type=helper.checkDir,default='.')
    parser.add_argument('-s','--suffixes', help='a comma separated list of suffixes the same length as the fastqFiles to use for a suffix in creating output files e.g. R1,R2',required=True,type=commaSep)
    parser.add_argument("-d","--dots", help="output dot to stderr every X reads. Input a negative number to suppress output (default:-1)", default=-1,type=int)
    parser.add_argument('-a','--append', help='if set then append to already existing output files',action='store_true')
    args=parser.parse_args(argv)

    if(len(args.suffixes)!=len(args.fastqFiles)):
        raise parser.error('Suffixes must be same length as fastqFiles')
    if args.append: mode='a'
    else: mode='w'

    barcodeSampleDict={xx[0]:xx[1] for xx in helper.readSimpleCsv(args.barcodeAssignments)}
    uniqSamples=set(barcodeSampleDict.values())
    outFiles={sample:[helper.openNormalOrGz(args.outputPath + '/' + sample+'_'+suffix+'.fastq.gz',mode) for suffix in args.suffixes] for sample in uniqSamples}
    
    with barcodeFastqIter(args.fastqFiles,args.barcodeCorrections,barcodeSampleDict) as fastqIter:
        for reads,sample,barcode in fastqIter:
            for read,outFile in zip(reads,outFiles[sample]):
                helper.writeFastqRead(outFile,read)
            if args.dots>0:
                if (fastqIter.nAssigned) % args.dots==0:
                    sys.stderr.write('.')
                    sys.stderr.flush()
    if args.dots>0:
        sys.stderr.write("\nAssigned reads: "+str(fastqIter.nAssigned)+" Unassigned reads: "+str(fastqIter.nUnassigned)+" Bad barcode reads: "+str(fastqIter.nBadBarcode)+"\n")
    for outFile in outFiles.values(): helper.closeFiles(outFile)

if __name__ == '__main__':
    main()
