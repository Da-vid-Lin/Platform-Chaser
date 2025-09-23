import json

file = open("PlatformPlayer/score.json","r")
data = file.readlines()
file.close()

leaderboards = json.loads(data[0])

lvl1 = leaderboards["lvl1"]

lvl0 = [["bob",100],["mashu",120],["bonk",200],["lin",999],["artoria",1002]] 

insert = ["potato",5]

main = []
temp = []

for data in lvl0:
    if data[1] <= insert[1]:
        main.append(data)
    else:
        temp.append(data)

main.append(insert)
main = main + temp

print(main)

