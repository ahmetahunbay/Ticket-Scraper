import binascii

my_string = "example"
my_id = binascii.crc32(my_string.encode()) & 0xffffffff
print(my_id)