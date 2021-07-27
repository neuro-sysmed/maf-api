
import maf.db as maf_db


def print_vcf(unannotated:bool=False) -> None:

    print("##fileformat=VCFv4.2")
    print("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO")
    for v in maf_db.variants():
        print("\t".join([v['chrom'], v['pos'], ".", v['ref'], v['alt'], '.','.','.']))