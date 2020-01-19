import Quote

q = Quote(
"<p>Be <b>conservative</b> in what you send, be <b>liberal</b> in what you accept</p>",
"https://192.168.64.2/2017/04/12/was-jesus-a-postel-christian/",
"https://en.wikipedia.org/wiki/Robustness_principle"
)

print(q.hash())

print(q.hashkey())

