using System;
using System.Text;

class Program {
    static uint _rotl32(uint x, int r) {
        return (x << r) | (x >> (32 - r));
    }

    static uint Murmur3_32(byte[] data, uint seed) {
        uint c1 = 0xCC9E2D51;
        uint c2 = 0x1B873593;
        uint h1 = seed;
        uint streamLength = 0;

        int i = 0;
        while (i < data.Length) {
            int chunkLength = Math.Min(4, data.Length - i);
            streamLength += (uint)chunkLength;
            uint k1 = 0;
            if (chunkLength == 4) {
                k1 = BitConverter.ToUInt32(data, i);
                k1 *= c1;
                k1 = _rotl32(k1, 15);
                k1 *= c2;
                h1 ^= k1;
                h1 = _rotl32(h1, 13);
                h1 = h1 * 5 + 0xE6546B64;
            } else if (chunkLength == 3) {
                k1 = (uint)(data[i] | (data[i + 1] << 8) | (data[i + 2] << 16));
                k1 *= c1;
                k1 = _rotl32(k1, 15);
                k1 *= c2;
                h1 ^= k1;
            } else if (chunkLength == 2) {
                k1 = (uint)(data[i] | (data[i + 1] << 8));
                k1 *= c1;
                k1 = _rotl32(k1, 15);
                k1 *= c2;
                h1 ^= k1;
            } else if (chunkLength == 1) {
                k1 = data[i];
                k1 *= c1;
                k1 = _rotl32(k1, 15);
                k1 *= c2;
                h1 ^= k1;
            }
            i += 4;
        }

        h1 ^= streamLength;
        h1 ^= h1 >> 16;
        h1 *= 0x85EBCA6B;
        h1 ^= h1 >> 13;
        h1 *= 0xC2B2AE35;
        h1 ^= h1 >> 16;
        return h1;
    }

    static void Main() {
        string path = "natives/stm/_chainsaw/message/dev1_term/dev1_term_menu.msg.22";
        byte[] lower = Encoding.Unicode.GetBytes(path.ToLower());
        byte[] upper = Encoding.Unicode.GetBytes(path.ToUpper());
        uint h1 = Murmur3_32(upper, 0xFFFFFFFF);
        uint h2 = Murmur3_32(lower, 0xFFFFFFFF);
        ulong hash = ((ulong)h1 << 32) | h2;
        Console.WriteLine(string.Format("Hash 1 (no slash): 0x{0:X16}", hash));
        
        path = "/" + path;
        lower = Encoding.Unicode.GetBytes(path.ToLower());
        upper = Encoding.Unicode.GetBytes(path.ToUpper());
        h1 = Murmur3_32(upper, 0xFFFFFFFF);
        h2 = Murmur3_32(lower, 0xFFFFFFFF);
        ulong hash2 = ((ulong)h1 << 32) | h2;
        Console.WriteLine(string.Format("Hash 2 (slash): 0x{0:X16}", hash2));
    }
}
