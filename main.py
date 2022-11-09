input = """
....3.58.
.6...5...
..5...2.4
3.29..7..
..9...6..
..6..81.2
5.4...3..
...2...7.
218.5....
"""

input = input.strip().split("\n")


#store the lines in a list of lists
size=9

control=set([str(x) for x in range(1,size+1)])





def indexToBlock(i, j):
    indexOfBlock = (i//3)*3 + j//3
    indexInBlock = (i%3)*3 + j%3
    return  (indexOfBlock, indexInBlock)

def blockToIndex(blockIndex, indexInBlock):
    # blockIndex/3 gives initial vertical displacement: which multiple of 3
    # indexInBlock/3 gives additional displacement
    i = 3*(blockIndex//3) + indexInBlock//3
    # blockIndex%3 gives initial horizontal displacement
    # indexInBlock%3 gives additional displacement
    j = 3*(blockIndex%3) + indexInBlock%3
    return (i,j)

def setDiff (setA, setB):
    return setA - setB
    

# list will be a list of lists of sets    
def isDone (list):
    value = True
    for i in range (0, len(list)):
        for j in range (0, len(list[i])):
            value = value and (len(list[i][j])) == 0
            if value == False: return False
    return value




# variables are in: horiz, vert, block
# create a data structure which maps coordinate pairs to possible values.

possible=[[set([str(x) for x in range(1,size+1)]) for x in range(0, size)] for x in range(0, size)]


horiz=[[] for x in range(0, size)]
for i, line in enumerate (input):
    lineClean = line.strip()
    for char in lineClean[:]:
        horiz[i].append (char);


# first build data structures to keep track of which fields have holes

# initialise for vertical lines.
# also blocks of 3
vert=[[0 for x in range (0, size)] for x in range(0, size)]
#print "vert=",vert
block=[[0 for x in range (0, size)] for x in range(0, size)]
#print "block=",block

for i in range (0, size):
    for j in range(0,size):
        vert[j][i] = horiz[i][j]
        x,y = indexToBlock (i,j)
        block[x][y] = horiz[i][j]



#print vert
#print block




# returns true if horiz[i][j] is the only place that this item can go
# we assume that this is a partially filled grid
# so we do not need to check for horizontal, vertical, block etc. 
def isOnlyCell (i, j, item):
    if horiz[i][j] != '.': return False
    x,y = indexToBlock (i,j)
    # test all of the squares in the block
    # if this item was in any of the other squares,
    # would it invalidate?
    value = True
    # first of all, has to be blank
    #print "[",i,"][",j,"]: Checking item ",item," against ",horiz[i][j]
    value = value and (horiz[i][j] == '.')
    # must be not already in the horizontal
    #print "[",i,"][",j,"]Checking item ",item," against ",horiz[i]
    value = value and item not in horiz[i]
    # must be not already in the vertical
    #print "[",i,"][",j,"]Checking item ",item," against ",vert[j]
    value = value and item not in vert[j]
    # if the item can't be in any of the blanks,
    # this function must return true. 
    if value == False: return value
    for t in range (0, size):
        if block[x][t] == '.': # a blank
            i2, j2 = blockToIndex (x,t)
            if not ((i2 == i) and (j2  == j)): 
                value = value and item in horiz[i2]
                if value == False:
                    value = item in vert[j2]
                if value == False: return value
    return value

def verify():
    value = True
    for i in range (0, size):
        value = value and (control - set(horiz[i]) == set([]))
        value = value and (control - set(vert[i]) == set([]))
        value = value and (control - set(block[i]) == set([]))
    return value



def setItem(i,j,item):
    horiz[i][j] = item
    vert[j][i] = item
    x,y = indexToBlock (i,j)
    block[x][y] = item
    possible[i][j] = set([])


def format (listOfLists):
    for i in range (0, size):
        print(i,)
    print("")
    for i in range (0, size):
        print("-",)
    print("")
    for i in range (0, size):
        for j in range (0, size):
            print(listOfLists[i][j],)
        print("i=",i)


# easier to check each 3x3 block. 
# first round of elimination takes out all the obvious 

for x in range (0, size):
    # before doing anything else remove all the items
    # from the possible vector which are already in this block
    inThisBlock = set(block[x])
    for y in range (0, size):
        # iterate over each block.
        
        item = block[x][y]
        i,j = blockToIndex (x,y)
        if item == '.':
            # we don't know what goes here
            possible[i][j] = setDiff (possible[i][j], inThisBlock)
            possible[i][j] = setDiff (possible[i][j], set(horiz[i]))
            possible[i][j] = setDiff (possible[i][j], set(vert[j]))

            if len(possible[i][j]) == 1:
                item = list(possible[i][j])[0]
                setItem (i,j,item)
                
        else:
            possible[i][j] = set([])
print("After initial pass:")
format (horiz)

print("Beginning more passes")

t = 0

# keep doing this until there are no more holes
while not isDone (possible):

    counter = 0 # use this to keep track of how many things changed in elimination
    for i in range (0, size):
        for j in range (0, size):
            x,y = indexToBlock (i,j)

            # First, eliminate anything that is already placed            
            possible[i][j] = possible[i][j] - set(horiz[i])
            possible[i][j] = possible[i][j] - set(vert[j])
            possible[i][j] = possible[i][j] - set(block[x])
            #print "[",i,"][",j,"] After filtering, possible values are ",possible[i][j]    

            # if we have eliminated everything except one item,
            # that is the correct item
            if len(possible[i][j]) == 1:
                item = list(possible[i][j])[0]
                setItem (i,j,item)
                counter = counter+1
                print("Row/column/block elimination: set item[",i,"][",j,"] to ",item," block is ",block[x])


            # The next check is to see if an item is the only one that can
            # fit in a cell. Do this by brute force: check if it can go into
            # any other cell in that block. 
            # only do the next check if a hole has not been filled
            if horiz[i][j] == '.':
                lp = list(possible[i][j])
                for p in range (0, len(lp)):
                    item = lp[p]
                    #print "Checking item ",item," against cell[",i,"][",j,"]"
                    if isOnlyCell (i,j,item):
                        # now we want to remove it and break
                        setItem (i,j,item)
                        counter = counter+1
                        print("2nd-order block elimination: Set item[",i,"][",j,"] to ",item)
                        break
    print("After elimination pass ",t)
    #format (possible)
    format (horiz)


    # the last test is to look at all the possible values in each row
    if counter == 0:
        for i in range (0, size):
            # will need to iterate a few times over the same row. 
            union = set([])
            for j in range (0, size):
                # first, get the set that is the union of all the possible values
                # for this row
                union = union | possible[i][j]
            unionlist = list(union)
            dictionary = dict([(unionlist[t],[]) for t in range(0, len(unionlist))])
            # keys of the dictionaries: possible items
            # values: cells that can have the key as a possible value
            for j in range (0, size):
                lp = list (possible[i][j])
                # Iterate over all of the possible values.
                # build up the dictionary
                for k in range (0, len (lp)):
                    val = dictionary[lp[k]]
                    val.append (j)
                    
            for j in range (0, size):
                lp = list (possible[i][j])
                for k in range (0, len(lp)):
                    # look up the value from the dictionary
                    otherIndexes = dictionary[lp[k]]
                    if len(otherIndexes) == 1:
                        print("Item ",lp[k]," present only in possible[",i,"][",j,"]")
                
                        x,y = indexToBlock (i,j)
                        item = lp[k]
                        if (possible[i][j] != [] and
                            item not in set(horiz[i]) and
                            item not in set(vert[j]) and
                            item not in set(block[x])):
                            setItem (i,j,item)
                            print("Pass ",t," guess: Set item[",i,"][",j,"] to ",item,", row is ",horiz[i]," column is ", vert[j]," block is ",block[x])
                            break;
                        else: print("Pass ",t," guess: CANNOT SET item[",i,"][",j,"] to ",item,", row is ",horiz[i]," column is ", vert[j]," block is ",block[x]," possible is ",possible[i][j])
                    
    
        print("After guess pass ",t)
        #format (possible)

        format (horiz)
    t = t+1

print("Done after ",t-1," passes")
print("Verified: ",verify ())
#format (possible)
#format (horiz)


            
            
            



