import os.path
start =  int(input("start_no "))
end = int(input("end_no "))

for i in range(start,end+1):
    filename = "page_" + str(i).zfill(5)+ ".txt"
	
    if not os.path.isfile(filename):
        print(filename + " is misssing")
