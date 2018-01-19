#!/usr/bin/python
# -*- coding: utf-8 -*-


input_zip_col = "a00001.zip"
input_zip_row = "a00002.zip"
unzip_dir_col = "unzip_dir_col"
unzip_dir_row = "unzip_dir_row"

keyword_count_limit = 30
output_file = "keyword_similarity.tsv"


#-------------------------------------------------
# Sub Functions
#-------------------------------------------------
def get_cluster_list(zipfile, unzip_dir):
	import commands

	cluster = []

	tsv = "mission.info.all.tsv"
	path = unzip_dir+"/"+tsv
	if not os.path.exists(path):
		command = 'unzip '+zipfile+' '+tsv+' -d \"'+unzip_dir+'\"'
		res = commands.getoutput(command)

	cc = 0
	f = open(path, 'r')
	for line in f.readlines():
		line = line.rstrip()
		cell = line.split('\t')

		if cell[0] == "cluster_count":
			cc = int(cell[1])
			break

	for i in range(1, cc+1):
		cluster.append(str(i))

	return cluster


def get_cluster_score(zipfile, unzip_dir, clist):
	import commands

	score = {}

	for c in clist:
		tsv = "mission.keyword."+c+".tsv"
		path = unzip_dir+"/"+tsv
		if not os.path.exists(path):
			command = 'unzip '+zipfile+' '+tsv+' -d \"'+unzip_dir+'\"'
			res = commands.getoutput(command)

		f = open(path, 'r')
		line1st = f.readline()

		i = 1
		for line in f.readlines():
			line = line.rstrip()
			cell = line.split('\t')
			
			score.setdefault(c, {})
			score[c][cell[0]] = float(cell[1])

			i += 1
			if i > keyword_count_limit:
				break

	return score


#-------------------------------------------------
# Functions
#-------------------------------------------------
def cal_score(CLIST_COL, SCORE_COL, CLIST_ROW, SCORE_ROW):
	import math
	import os
	import re
	import sys

	############################################################
	### calculate similarity
	SIM = {}
	for a in CLIST_ROW:
		SCORE_ROW.setdefault(a, {})

		for b in CLIST_COL:
			inner_ab = 0.0
			normsq_a = 0.0
			normsq_b = 0.0
			SCORE_COL.setdefault(b, {})

			ALL_KEYWORDS = []
			for k, v in SCORE_ROW[a].items():
				ALL_KEYWORDS.append(k)
			for k, v in SCORE_COL[b].items():
				ALL_KEYWORDS.append(k)
			ALL_KEYWORDS = set(ALL_KEYWORDS)
			for k in ALL_KEYWORDS:
				SCORE_ROW[a].setdefault(k, 0.0)
				SCORE_COL[b].setdefault(k, 0.0)

				inner_ab += SCORE_ROW[a][k] * SCORE_COL[b][k]
				normsq_a += SCORE_ROW[a][k] * SCORE_ROW[a][k]
				normsq_b += SCORE_COL[b][k] * SCORE_COL[b][k]

			if normsq_a > 0.0 and normsq_b > 0.0:
				SIM.setdefault(a, {})
				SIM[a][b] = inner_ab / (math.sqrt(normsq_a) * math.sqrt(normsq_b))

	return SIM



#-------------------------------------------------
# Main Routine
#-------------------------------------------------
import os
import re
import sys

CLIST_COL = get_cluster_list(input_zip_col, unzip_dir_col)
CLIST_ROW = get_cluster_list(input_zip_row, unzip_dir_row)
SCORE_COL = get_cluster_score(input_zip_col, unzip_dir_col, CLIST_COL)
SCORE_ROW = get_cluster_score(input_zip_row, unzip_dir_row, CLIST_ROW)
SIM = cal_score(CLIST_COL, SCORE_COL, CLIST_ROW, SCORE_ROW)

f = open(output_file, 'w')
for a in sorted(SIM.keys()):
	for b, s in SIM[a].items():
		f.write(a+"\t"+b+"\t"+str(s)+"\n")
f.close()
