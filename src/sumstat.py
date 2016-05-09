# (c) 2016-2021 Huwenbo Shi


import sys


# define equivalence alleles
equiv = dict()
equiv["AC"] = set(["TG", "AC", "TC", "AG"])
equiv["AG"] = set(["TC", "AG", "TG", "AC"])
equiv["CA"] = set(["GT", "CA", "GA", "CT"])
equiv["CT"] = set(["GA", "CT", "GT", "CA"])
equiv["TC"] = set(["AG", "TC", "AC", "TG"])
equiv["TG"] = set(["AC", "TG", "AG", "TC"])
equiv["GA"] = set(["CT", "GA", "CA", "GT"])
equiv["GT"] = set(["CA", "GT", "CT", "GA"])


# define reversed alleles
reverse = dict()
reverse["AC"] = set(["GT", "CA", "CT", "GA"])
reverse["AG"] = set(["CT", "GA", "GT", "CA"])
reverse["CA"] = set(["TG", "AC", "AG", "TC"])
reverse["CT"] = set(["AG", "TC", "TG", "AC"])
reverse["TC"] = set(["GA", "CT", "CA", "GT"])
reverse["TG"] = set(["CA", "GT", "GA", "CT"])
reverse["GA"] = set(["TC", "AG", "AC", "TG"])
reverse["GT"] = set(["AC", "TG", "TC", "AG"])


# define strand ambiguous alleles
ambiguous = set(["AT", "CG", "TA", "GC"])


"""
description:
    filter out any snp in z-score file that is not in reference panel
    filter out any snp with strand ambiguilty
    fix the sign of beta to be consistent with reference panel
arguments:
    1. refpanel_leg (list) - a list of snp (rsids, ref_alt) in the legend
    2. snp_beta (dict) - a dictionary that maps snps with beta
    3. snp_beta_info (list) - a list of (rsid, pos, n, ref_alt)
return:
    1. a dictionary mapping snp id with beta with sign fixed
    2. a list of filtered (snpid, pos, n, ref_alt)
"""
def filter_snps(refpanel_leg, snp_beta, snp_beta_info):
    
    # create a dictionary of snpid -> refalt
    snpid_refpanel_refalt = dict()
    for snpid,refalt in refpanel_leg:
        snpid_refpanel_refalt[snpid] = refalt
    
    # count number of entry with the same rs id
    rsid_pos_cnt = dict()
    for i in xrange(len(snp_beta_info)):
        snpid = snp_beta_info[i][0]
        if(snpid not in rsid_pos_cnt):
            rsid_pos_cnt[snpid] = 1
        else:
            rsid_pos_cnt[snpid] += 1

    # count the number of rsid with the same pos
    pos_rsid_cnt = dict()
    for i in xrange(len(snp_beta_info)):
        snppos = snp_beta_info[i][1]
        if(snppos not in pos_rsid_cnt):
            pos_rsid_cnt[snppos] = 1
        else:
            pos_rsid_cnt[snppos] += 1
    
    # find snps to be removed
    filter_set = set()
    for i in xrange(len(snp_beta_info)):
        snpid = snp_beta_info[i][0]
        snppos = snp_beta_info[i][1]
        refalt = snp_beta_info[i][3]
        
        # check if snp is in reference panel
        if(snpid in snpid_refpanel_refalt):
            refpanel_refalt = snpid_refpanel_refalt[snpid]
            
            # snps with matching alleles, do nothing
            if((refpanel_refalt == "AC" and refalt in equiv["AC"]) or
               (refpanel_refalt == "AG" and refalt in equiv["AG"]) or
               (refpanel_refalt == "CA" and refalt in equiv["CA"]) or
               (refpanel_refalt == "CT" and refalt in equiv["CT"]) or
               (refpanel_refalt == "TC" and refalt in equiv["TC"]) or
               (refpanel_refalt == "TG" and refalt in equiv["TG"]) or
               (refpanel_refalt == "GA" and refalt in equiv["GA"]) or
               (refpanel_refalt == "GT" and refalt in equiv["GT"])):
                pass
            # snps with inverse alleles, multiply z-score with -1
            elif((refpanel_refalt == "AC" and refalt in reverse["AC"]) or
                 (refpanel_refalt == "AG" and refalt in reverse["AG"]) or
                 (refpanel_refalt == "CA" and refalt in reverse["CA"]) or
                 (refpanel_refalt == "CT" and refalt in reverse["CT"]) or
                 (refpanel_refalt == "TC" and refalt in reverse["TC"]) or
                 (refpanel_refalt == "TG" and refalt in reverse["TG"]) or
                 (refpanel_refalt == "GA" and refalt in reverse["GA"]) or
                 (refpanel_refalt == "GT" and refalt in reverse["GT"])):
                snp_beta[snpid] = -1.0*snp_beta[snpid]
            # strand ambiguous snps
            elif(refalt in ambiguous):
                filter_set.add(i)
            # snps with alleles not matching reference panel
            else:
                filter_set.add(i)
        # snp not found in reference panel
        else:
            filter_set.add(i)
        
        # check for snp with ambiguous position
        if(rsid_pos_cnt[snpid] > 1):
            filter_set.add(i)
        if(pos_rsid_cnt[snppos] > 1):
            filter_set.add(i)
    
    # create new snp_beta snp_beta_info
    snp_beta_filt = dict()
    snp_beta_info_filt = []
    for i in xrange(len(snp_beta_info)):
        if(i not in filter_set):
            snpid = snp_beta_info[i][0]
            snp_beta_filt[snpid] = snp_beta[snpid]
            snp_beta_info_filt.append(snp_beta_info[i])

    return snp_beta_filt,snp_beta_info_filt
