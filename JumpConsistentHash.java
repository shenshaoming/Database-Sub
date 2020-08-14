
/**
 * 原C++实现：
 *
 * 传入一个64位的key，和32位的桶的数量（对应数据源节点的数量）
 * 返回一个桶的编号
 *
    int32_t JumpConsistentHash(uint64_t key, int32_t num_buckets) {
        int64_t b = -1, j = 0;
        while (j < num_buckets) {
            b = j;
            key = key * 2862933555777941757ULL + 1;
            j = (b + 1) * (double(1LL << 31) / double((key >> 33) + 1));
        }
        return b;
    }
 *
 */


/**
 * @author ssm
 * @version 1.0
 * @className JumpConsistentHash
 * @date 2020/8/14 14:57
 */
public class JumpConsistentHash {

    private static final long UNSIGNED_MASK = 0x7fffffffffffffffL;

    private static final long JUMP = 1L << 31;

    private static final long CONSTANT = Long.parseUnsignedLong("2862933555777941757");

    /**
     *
     * @param object 要存储使用的分片键
     * @param number 数据库节点数量
     * @return 数据库节点编号
     */
    public static int jumpConsistentHash(final Object object, final int number) {
        return jumpConsistentHash((long) object.hashCode(), number);
    }

    /**
     *
     * @param key 要存储使用的分片键 long类型
     * @param number 数据库节点数量
     * @return 数据库节点编号
     */
    public static int jumpConsistentHash(final Long key, final int number) {
        checkBuckets(number);
        long k = key;
        long b = -1;
        long j = 0;

        while (j < number) {
            b = j;
            k = k * CONSTANT + 1L;

            j = (long) ((b + 1L) * (JUMP / toDouble((k >>> 33) + 1L)));
        }
        return (int) b;
    }

    /**
     * 数据库节点数量不能小于0
     *
     * @param number
     */
    private static void checkBuckets(final int number) {
        if (number < 0) {
            throw new IllegalArgumentException("Buckets cannot be less than 0");
        }
    }

    private static double toDouble(final long n) {
        double d = n & UNSIGNED_MASK;
        if (n < 0) {
            d += 0x1.0p63;
        }
        return d;
    }
}
