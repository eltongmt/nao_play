import qi

s = qi.Session()
s.connect("tcp://192.168.1.65:9559")

s.service("Foo")