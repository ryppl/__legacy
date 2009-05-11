//
// pointers point to things that are aligned on certain
// boundaries... you can hash them by chopping off the zero bits on
// the right.  Found this on the net somewhere.
//
//
namespace detail {
    const unsigned nbuckets = 1024; 
    const unsigned hash_mask = nbuckets-1; // 0x3FF if nbuckets is 1024

    struct type_info_ptr_hash
    {
	size_t operator()( const std::type_info* p) const
	{
	    return (reinterpret_cast<size_t>(p) >> 6) & hash_mask;
	}
    };
}

std::unordered_map<const std::type_info*, 
		   std::string, 
		   detail::type_info_ptr_hash>  storage_t;

