# Huffman Compression Algorithm
Author: James Chen

I have designed a Huffman compression algorithm in python to compress my data. The algorithm through several the following steps:
1.	Converts the bytes into a nested list forest
2.	Sort/branches the nodes to create a Huffman tree
3.	Recursively goes through the tree and assigns each unique byte with a code
4.	Compresses message data

    The compressed message has the following format:
    i.	Bytes 0-3 indicate message length
    ii.	Byte 4 indicates number of elements in the decoder
    iii.	Next bytes give encoding,  dictionary and original byte
    iv.	After this, remaining bytes indicate compressed message (able to be decoded with previous data)

See docstrings and comments for more detailed explanation.
