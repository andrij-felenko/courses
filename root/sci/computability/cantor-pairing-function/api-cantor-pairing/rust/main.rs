   #[repr(C)]
   pub struct CantorPair32 {
       pub x: u32,
       pub y: u32,
   }

   extern "C" {
       pub fn cantor_encode32(x: u32, y: u32, out_code: *mut u64) -> i32;
       pub fn cantor_decode32(code: u64, out_pair: *mut CantorPair32) -> i32;
   }
