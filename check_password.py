

# rf = open('rockyou.txt', 'r', errors="ignore")
# S = []
# for line in rf:
#     if line.isascii():
#         S.append(line.strip())

# if len(S) != 0:
#     x = open('rockyouASCII.txt', 'w')
#     x.write("\n".join(S))
with open('rockyouASCII.txt') as f:
    S = []
    for l in f:
        S.append(l.strip())