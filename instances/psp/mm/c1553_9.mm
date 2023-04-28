************************************************************************
file with basedata            : c1553_.bas
initial value random generator: 1111967114
************************************************************************
projects                      :  1
jobs (incl. supersource/sink ):  18
horizon                       :  131
RESOURCES
  - renewable                 :  2   R
  - nonrenewable              :  2   N
  - doubly constrained        :  0   D
************************************************************************
PROJECT INFORMATION:
pronr.  #jobs rel.date duedate tardcost  MPM-Time
    1     16      0       21        7       21
************************************************************************
PRECEDENCE RELATIONS:
jobnr.    #modes  #successors   successors
   1        1          3           2   3   4
   2        3          1          12
   3        3          1          11
   4        3          3           5   6   7
   5        3          2           8  13
   6        3          3           9  10  11
   7        3          3          15  16  17
   8        3          1          10
   9        3          1          14
  10        3          1          14
  11        3          1          13
  12        3          1          14
  13        3          1          17
  14        3          2          15  16
  15        3          1          18
  16        3          1          18
  17        3          1          18
  18        1          0        
************************************************************************
REQUESTS/DURATIONS:
jobnr. mode duration  R 1  R 2  N 1  N 2
------------------------------------------------------------------------
  1      1     0       0    0    0    0
  2      1     1       4    5    7    9
         2    10       1    3    1    9
         3    10       3    4    3    8
  3      1     3       5    6    3    5
         2     8       4    6    2    4
         3    10       4    6    1    2
  4      1     3       9    3    5    2
         2     7       8    3    5    1
         3    10       7    3    4    1
  5      1     2       5    4    8    5
         2    10       3    2    8    5
         3    10       3    3    7    4
  6      1     1       4    8    5    8
         2     3       3    5    5    3
         3     9       2    2    5    1
  7      1     3       8    7    9   10
         2     3       9    7    9    9
         3     7       7    5    9    8
  8      1     4       9    9    7    7
         2     5       7    9    7    6
         3    10       6    8    4    6
  9      1     1      10    8    5    6
         2     2       9    7    5    6
         3     6       9    6    4    4
 10      1     2       4    9    6    4
         2     4       3    9    5    4
         3     7       3    8    5    4
 11      1     3       6    9    4    9
         2     5       6    6    4    8
         3     7       5    3    3    6
 12      1     3       7    8    9    4
         2     5       7    5    8    4
         3     8       7    3    4    3
 13      1     9       7   10    9    7
         2     9       8    7   10    7
         3    10       5    5    6    6
 14      1     2       5    5    5    2
         2     3       5    5    4    2
         3     4       5    4    2    2
 15      1     3       9    5    7    6
         2     3       8    6    7    6
         3     6       8    4    5    6
 16      1     8       4    9    5    5
         2     9       3    7    3    1
         3     9       3    7    1    4
 17      1     3       8    6    5    9
         2     4       5    6    3    7
         3     8       3    6    2    7
 18      1     0       0    0    0    0
************************************************************************
RESOURCEAVAILABILITIES:
  R 1  R 2  N 1  N 2
   14   13   91   91
************************************************************************