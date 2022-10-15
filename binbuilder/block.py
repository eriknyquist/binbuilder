
class DataType(object):
    """
    Enumerates all available atomic data types
    """
    INT_1B = 0
    INT_2B = 1
    INT_4B = 2
    INT_8B = 3
    UINT_1B = 4
    UINT_2B = 5
    UINT_4B = 6
    UINT_8B = 7
    FLOAT = 8
    DOUBLE = 9
    BYTES = 10


class DataTypeInfo(object):
    """
    Represents all required information about a single atomic datatype
    """
    def __init__(self, datatype, size_bytes, name, pystruct_name, c_name):
        self.datatype = datatype
        self.size_bytes = size_bytes
        self.name = name
        self.pystruct_name = pystruct_name
        self.c_name = c_name


# Mapping of DataType enum values to DataTypeInfo objects
DATATYPES = {
    DataType.INT_1B: DataTypeInfo(DataType.INT_1B, 1, "signed integer (1 byte)",  "b", "int8_t {name}"),
    DataType.INT_2B: DataTypeInfo(DataType.INT_2B, 2, "signed integer (2 bytes)",  "h", "int16_t {name}"),
    DataType.INT_4B: DataTypeInfo(DataType.INT_4B, 4, "signed integer (4 bytes)",  "i", "int32_t {name}"),
    DataType.INT_8B: DataTypeInfo(DataType.INT_8B, 8, "signed integer (8 bytes)",  "q", "int64_t {name}"),
    DataType.UINT_1B: DataTypeInfo(DataType.UINT_1B, 1, "unsigned integer (1 byte)",  "B", "uint8_t {name}"),
    DataType.UINT_2B: DataTypeInfo(DataType.UINT_2B, 2, "unsigned integer (2 bytes)",  "H", "uint16_t {name}"),
    DataType.UINT_4B: DataTypeInfo(DataType.UINT_4B, 4, "unsigned integer (4 bytes)",  "I", "uint32_t {name}"),
    DataType.UINT_8B: DataTypeInfo(DataType.UINT_8B, 8, "unsigned integer (8 bytes)",  "Q", "uint64_t {name}"),
    DataType.FLOAT: DataTypeInfo(DataType.FLOAT, 4, "float (4 bytes)",  "f", "float {name}"),
    DataType.DOUBLE: DataTypeInfo(DataType.DOUBLE, 8, "double (8 bytes)",  "d", "double {name}"),
    DataType.BYTES: DataTypeInfo(DataType.BYTES, None, "bytes (arbitrary length)",  "s{parameter}", "uint8_t {name}[{parameter}]")
}


def string_to_varname(s):
    """
    Convert an ASCII string to a valid C variable name

    :param str s: string to convert

    :return: variable name
    :rtype: str
    """
    ret = ""

    for i in range(len(s)):
        if s[i].isdigit():
            if len(ret) == 0:
                continue
            else:
                ret += s[i]

        elif s[i].isalpha():
            ret += s[i].lower()

        else:
            if (len(ret) > 1) and (ret[-1] != "_"):
                ret += "_"

    return ret


class Block(object):
    """
    Represents a single data field of a particular atomic data type
    """
    def __init__(self, datatype=DataType.UINT_4B, name="", default_value=0, parameter=None, varname_prefix=''):
        self.typeinfo = None
        self.set_type(datatype)

        self.name = None
        self.varname = None
        self.varname_prefix = varname_prefix
        self.set_name(name)

        self.varname_prefix = varname_prefix
        self.value = default_value
        self.parameter = parameter

    def set_name(self, name):
        self.name = name
        self.varname = self.varname_prefix + string_to_varname(name)

    def set_type(self, datatype):
        self.typeinfo = DATATYPES[datatype]

    def set_value_string(self, value):
        if self.typeinfo.datatype in [DataType.FLOAT, DataType.DOUBLE]:
            self.value = float(value)
        elif self.typeinfo.datatype == DataType.BYTES:
            self.value = bytes.fromhex(value)
            self.parameter = len(self.value)
        else:
            self.value = int(value)

    def value_string(self):
        if self.typeinfo.datatype in [DataType.FLOAT, DataType.DOUBLE]:
            return f"{self.value:.4f}"
        elif self.typeinfo.datatype == DataType.BYTES:
            return " ".join([f"{b:02X}" for b in self.value])

        return str(self.value)

    def size_bytes(self):
        if DataType.BYTES == self.typeinfo.datatype:
            return 0 if self.parameter is None else self.parameter

        return self.typeinfo.size_bytes


class BlockSequence(object):
    """
    Represents a sequence of data fields, containing multiple Block objects
    """
    def __init__(self, name, blocklist):
        # Check blocklist for dupe var names
        names = {}
        for b in blocklist:
            if b.varname in names:
                existing_name = names[b.varname]
                raise ValueError(f"blocks '{b.name}' and '{existing_name}' result in "
                                 f"the same C variable name, use names that are more different")

        self.name = None
        self.varname = None
        self.set_name(name)

        self.blocklist = blocklist

    def set_name(self, name):
        self.name = name
        self.varname = string_to_varname(name)

    def _index_by_name(self, name):
        varname = string_to_varname(name)
        for i in range(len(self.blocklist)):
            if self.blocklist[i].varname == varname:
                return i

        raise ValueError(f"No such name '{name}'")

    def get_block_by_name(self, name):
        return self.blocklist[self._index_by_name(name)]

    def remove_block_by_name(self):
        del self.blocklist[self._index_by_name]

    def reorder_by_names(self, names):
        new_blocklist = []
        for n in names:
            # Read block by name from the old list, and
            # append to the new list in the correct position
            new_blocklist.append(self.get_block_by_name(n))

        self.blocklist = new_blocklist

    def size_bytes(self):
        return sum([b.size_bytes() for b in self.blocklist])

    def add_block(self, block):
        for b in self.blocklist:
            if block.varname == b.varname:
                raise ValueError("This sequence already has a block with the same"
                                 "C variable name, use a different name")

        self.blocklist.append(block)

    def generate_c_defaults(self):
        lines = []

        for block in self.blocklist:
            valstr = str(block.value)

            dtype = block.typeinfo.datatype

            if (dtype >= DataType.UINT_1B) and (dtype <= DataType.UINT_8B):
                valstr += "u"
            elif dtype == DataType.FLOAT:
                valstr += "f"
            elif dtype == DataType.BYTES:
                valstr = "{" + ", ".join(f"0x{b:02x}u" for b in block.value) + "}"

            lines.append(f"    .{block.varname}={valstr}")

        return ",\n".join(lines)

    def generate_c_string(self):
        lines = []

        for block in self.blocklist:
            block_kwargs = {
                "name": block.varname,
            }

            if block.parameter is not None:
                block_kwargs["parameter"] = block.parameter

            lines.append("    " + block.typeinfo.c_name.format(**block_kwargs) + ";")

        return "\n".join(lines)

    def generate_pystruct_fmtstring(self):
        ret = ""
        for block in self.blocklist:
            text = block.typeinfo.pystruct_name

            if block.parameter is not None:
                text = text.format(parameter=block.parameter)

            ret += text

        return ret


class Schema(object):
    """
    Represents a schema for a binary file, containing multiple BlockSequence objects
    """
    def __init__(self, name, sequencelist=[], big_endian=True):
        self.name = name
        self.sequencelist = sequencelist
        self.big_endian = big_endian

    def size_bytes(self):
        return sum([s.size_bytes() for s in self.sequencelist])

    def add_sequence(self, sequence):
        self.sequencelist.append(sequence)

    def generate_c_string(self):
        return '\n'.join([s.generate_c_string() for s in self.sequencelist])

    def generate_pystruct_fmtstring(self):
        return ''.join([s.generate_pystruct_fmtstring() for s in self.sequencelist])


class CodeWriter(object):
    def __init__(self, big_endian=True):
        self.big_endian = big_endian

    def generate_c_string(self, obj):
        ret = "typedef struct\n{\n"
        ret += obj.generate_c_string()

        structname = string_to_varname(obj.name) + "_t"
        ret += "\n} __attribute__((packed)) " + structname + ";\n"

        ret += "\n" + structname + " default = \n{\n"
        ret += obj.generate_c_defaults()
        ret += "\n};"

        return ret

    def generate_pystruct_fmtstring(self, obj):
        end = ">" if self.big_endian else "<"
        return end + obj.generate_pystruct_fmtstring()


def main():
    blocks = [
        Block(DataType.UINT_4B, "First Counter", 44),
        Block(DataType.UINT_4B, "Second Counter", 55),
        Block(DataType.DOUBLE, "THIRD,,::;;COUNTER", 55.5),
        Block(DataType.FLOAT, "fourth,  COUNTER", 55.5),
        Block(DataType.BYTES, "Auth. Token", b'ffff', 4),
        Block(DataType.BYTES, "AUTHKEY", b'ffffgggghhhhjjjj', 12)
    ]

    schema = Schema("Test Sequence", sequencelist=[BlockSequence("test", blocks)])
    print(schema.generate_pystruct_fmtstring())
    print(schema.generate_c_string())
    print(schema.size_bytes())

if __name__ == "__main__":
    main()

