import decimal
import csv

def printArray(data,n=0):
	print("get IN : ",n)
	if n==0:
		n = len(x)-1
	for i in range(n):
		print(data[n])

def openCSV(namafile, delimiter = ','):
	with open(namafile, 'r') as file:
	    datas = csv.reader(file, delimiter = delimiter)
	    data = []
	    for d in datas:
	        data.append(d)
	return data

def simpanCSV(namafile,data):
	with open(namafile, 'w', newline='') as file:
	    writer = csv.writer(file)
	    writer.writerows(data)

if __name__ == "__main__":
	print(frange(0, 100, '0.1'))