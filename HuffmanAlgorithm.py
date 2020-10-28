# Author: James Chen


def byte_compress(data_ptr, data_size):
    """
    Function implements a Huffman compression algorithm to compress a data duffer of bytes, this function is written as
     a 16 bit system, therefor the maximum data size  is 2^16 = 65 535. the compressed data is organized as follows:
    bytes 0-3: indicate original message length, up to 65535
    byte 4: indicates length of dictionary (max of 256)
    other bytes indicate the compression/decompression dictionary, followed by the encoded message.
    :param data_ptr: (bytearray) points to an array of bytes, each byte contains a number from 0 to 127 (0x00 to 0x7F) to be
            compressed
    :param data_size: (int) states how many bytes to compress
    :return: Modified buffer size (bytes)
    """
    # copy all bytes into list, convert into chars
    all_elements = list(data_ptr)
    for j in range(0, len(all_elements)):
        all_elements[j] = chr(all_elements[j])

    # create dictionary of frequencies (histogram)
    frequencies = dict()
    for byte in all_elements:
        if byte not in frequencies:
            frequencies[byte] = 1
        else:
            frequencies[byte] += 1

    # beginning of forest, unorganized
    tree = []
    for element in frequencies:
        el = [frequencies[element], element]
        tree.append(el)

    # organize into Huffman tree
    while len(tree) > 1:
        reduce_tree(tree)

    # Recursively find encodings for huffman tree
    decoder = dict()
    encoding = []
    tree_to_decoder(tree[0], decoder, encoding, len(frequencies))

    # add length of original message into output (bytes 0-3)
    number_of_input = [0xff & (data_size >> 24), 0xff & (data_size >> 16), 0xff & (data_size >> 8), 0xff & data_size]
    output_bytes = number_of_input

    # add length of dictionary in byte 4, NOTE actual dictionary length will be double of the length (code &message)
    output_bytes.append(len(decoder))

    # add dictionary to output bytes
    items = list(decoder)
    for item in items:
        output_bytes.append(decoder[item])
        output_bytes.append(ord(item))

    # compress messages into few bytes
    messages = all_elements[:]
    for j in range(0, len(messages)):
        messages[j] = decoder[messages[j]]

    compressed_message = [0]
    bits_used = 0
    byte_under_use = 0
    for bits in messages:  # store each encoded byte
        for bits_size in range(0, 8):  # check bit length
            max_size = 0
            for i in range(0, bits_size):  # calculate max size of bits
                max_size += 2 ** i
            if bits == 0:
                max_size = 1
                bits_size = 1

            if bits <= max_size:
                if bits_used + bits_size > 8:  # for splitting bytes
                    compressed_message[byte_under_use] += (bits >> (8 - bits_used))  # get rid of extra bits
                    byte_under_use += 1
                    cutter = 0
                    bits_needed = bits_size - (8 - bits_used)
                    for i in range(0, bits_needed):
                        cutter += 2 ** i
                    compressed_message.append((bits & cutter) << (8 - bits_needed))  # store cut off bits
                    bits_used = bits_needed
                else:  # no split required, all fit into same byte
                    compressed_message[byte_under_use] += (bits << (8 - bits_used - bits_size))
                    bits_used += bits_size
                    if bits_used == 8:  # if perfect fit, need to move to next byte
                        compressed_message.append(0)
                        bits_used = 0
                        byte_under_use += 1
                break

    # add message to output list
    output_bytes.extend(compressed_message)
    data_ptr[:] = bytearray(output_bytes)  # convert list into byte array

    return len(output_bytes)


def tree_to_decoder(tree, decoder, encoding, elements):
    """
    Recursive function to encode a organized Huffman tree in the form of a nested list
    :param tree: (list) Organized Huffman tree (nested lists)
    :param decoder: (dict) dictionary to convert message to encoded format
    :param encoding: (list) list, keeps track of movement up/down the list
    :param elements: (int) number of encodings needed (number of unique values)
    :return: (dict) dictionary to convert message to encoded format
    """
    # create new encoding lists so there is no data loss
    encoding1 = encoding[:]
    encoding1.append(0)
    encoding2 = encoding[:]
    encoding2.append(1)

    # if length is 3, need to go deeper into branch
    if len(tree) == 3:
        tree_to_decoder(tree[1], decoder, encoding1, elements)
        tree_to_decoder(tree[2], decoder, encoding2, elements)

    # if length is 2, we have reached a leaf, record encoding and return
    if len(tree) == 2:
        code = 0
        for base in range(0, len(encoding)):
            code += 2 ** base * encoding[len(encoding) - base - 1]
        decoder[tree[1]] = code

        return decoder


def reduce_tree(input_tree):
    """
    Takes nested list, reorganizes according to Huffman compression algorithm
    :param input_tree: (list) raw nested list, frequency in 0th index
    :return:
    """
    leafs = find_lowest_two_nodes(input_tree)

    new_branch = [leafs[0][0] + leafs[1][0], leafs[0], leafs[1]]  # create new branch

    input_tree.remove(leafs[0])  # remove old branches
    input_tree.remove(leafs[1])

    input_tree.append(new_branch)  # add new branch


def find_lowest_two_nodes(tree):
    """
    Takes a nested list tree as input, returns the lowest two nodes according to frequency
    node format should be: [frequency, branch/leaf, branch/leaf]
    :param tree: (list) nested list of nodes, frequency should be at 0 index, max length of 3 (1 frequency, 2 branches)
    :return: (tuple) returns tuple of the 2 lowest frequency lists, first element of tuple will have lowest frequency
    """
    lowest_two_nodes = []
    first_branch = 1
    for leaf in tree:
        if first_branch >= 0:  # store first 2 nodes no matter what
            lowest_two_nodes.append(leaf)
            first_branch -= 1
        else:  # after first 2, look check to see if node is lower. [0] will always be lower then leaf[1]
            if leaf[0] < lowest_two_nodes[0][0]:
                lowest_two_nodes[0] = leaf
            elif leaf[0] < lowest_two_nodes[1][0]:
                lowest_two_nodes[1] = leaf
    return lowest_two_nodes[0], lowest_two_nodes[1]


if __name__ == '__main__':
    # uncomment to see a random buffer bytes
    # byte_list = []
    # for i in range(0, 20):
    #     byte_list.append(randint(0, 127))

    # testing purposes
    byte_list = [110, 110, 111, 112, 112, 112, 112, 113]

    test_data_ptr = bytearray(byte_list)
    print("Input data bytes:")
    print(test_data_ptr)

    compressed_size = byte_compress(test_data_ptr, 8)

    print('New compressed size is: ')
    print(compressed_size)
    print("Compressed data: ")
    print(test_data_ptr)
