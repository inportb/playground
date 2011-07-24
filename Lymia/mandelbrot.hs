import Data.Array
import Data.Bits
import Data.List
import Data.Word
import qualified Codec.Compression.Zlib as Z
import qualified Data.ByteString.Lazy as B

import System.Environment 
import Data.Complex

-- Command Line Interface --

main = main' `catch` handler 

main' = do
    (size:xCenter:yCenter:zoom:iters:output:_) <- getArgs
    B.writeFile output $ png $ renderParse size xCenter yCenter zoom iters
renderParse size' xCenter' yCenter' zoom' iters' = 
    renderFractal size xCenter yCenter zoom iters
    where size    = parseInt    size'
          xCenter = parseDouble xCenter'
          yCenter = parseDouble yCenter'
          zoom    = parseDouble zoom'
          iters   = parseInt    iters'

handler e = do 
    progName <- getProgName
    putStrLn $ usageStr progName
usageStr p = "Usage: "++p++" [size] [x] [y] [zoom] [max iterations] [output]"

parseInt s = read s :: Int
parseDouble s = read s :: Double

-- Fractal Renderer --

renderFractal size xCenter yCenter zoom iters = 
    map (\y -> map (\x -> fracf $ (xCenter+x) :+ (yCenter+y)) range) range
    where fracf  = (color iters) . (mandelbrot iters)
          half   = (fromIntegral size) / 2
          tick   = (1 / (fromIntegral size)) * (4 / zoom)
          range  = map (tick*) [-half..half]

mandelbrot maxIters c = findIndex outside $ take maxIters $ iters
    where step z    = (z*z) + c
          double x  = x * x
          outside x = ((double $ imagPart x) + (double $ realPart x)) > 4
          iters     = iterate step $ 0 :+ 0

color maxIters' Nothing      = (0, 0, 0)
color maxIters' (Just iter') = 
    (floor(r*360),floor(g*360),floor(b*360))
    where maxIters   = fromIntegral maxIters'
          iter       = fromIntegral iter'
          hueStart   = 240.0
          hueRange   = -120.0
          saturation = 0.9
          value      = 1.0
          iterRatio  = (1.0 / maxIters)*iter
          (r, g, b)  = hsv (hueStart+(hueRange*iterRatio)) saturation value

------------------
-- Library Code --
------------------

-- From Data.Colour.RGB --
hsv :: (RealFrac a, Ord a) => a -> a -> a -> (a, a, a)
hsv h s v = case hi of
    0 -> (v, t, p)
    1 -> (q, v, p)
    2 -> (p, v, t)
    3 -> (p, q, v)
    4 -> (t, p, v)
    5 -> (v, p, q)
 where
  hi = floor (h/60) `mod` 6
  f = mod1 (h/60)
  p = v*(1-s)
  q = v*(1-f*s)
  t = v*(1-(1-f)*s)

mod1 x | pf < 0 = pf+1
       | otherwise = pf
 where
  (_,pf) = properFraction x

-- From http://haskell.org/haskellwiki/Library/PNG --

be8 :: Word8 -> B.ByteString
be8 x = B.singleton x
 
be32 :: Word32 -> B.ByteString
be32 x = B.pack [fromIntegral (x `shiftR` sh) | sh <- [24,16,8,0]]
 
pack :: String -> B.ByteString
pack xs = B.pack $ map (fromIntegral.fromEnum) xs
 
unpack :: B.ByteString -> String
unpack xs = map (toEnum.fromIntegral) (B.unpack xs)
 
hdr, iHDR, iDAT, iEND :: B.ByteString
hdr = pack "\137\80\78\71\13\10\26\10"
iHDR = pack "IHDR"
iDAT = pack "IDAT"
iEND = pack "IEND"
 
chunk :: B.ByteString -> B.ByteString -> [B.ByteString]
chunk tag xs = [be32 (fromIntegral $ B.length xs), dat, be32 (crc dat)]
    where dat = B.append tag xs
 
-- | Return a monochrome PNG file from a two dimensional bitmap
-- stored in a list of lines represented as a list of tuples of
-- 3 Ints.
png :: [[(Int,Int,Int)]] -> B.ByteString
png dat = B.concat $ hdr : concat [ihdr, imgdat ,iend]
     where height = fromIntegral $ length dat
           width = fromIntegral $ length (head dat)
           ihdr = chunk iHDR $ B.concat 
                     [ be32 height
                     , be32 width
                     , be8 8   -- bits per sample (8 for r, 8 for g, 8 for b)
                     , be8 2   -- color type (2=rgb)
                     , be8 0   -- compression method
                     , be8 0   -- filter method
                     , be8 0 ] -- interlace method
           imgdat = chunk iDAT (Z.compress imagedata)
           imagedata = B.concat $ map scanline dat
           iend = chunk iEND B.empty
 
scanline :: [(Int,Int,Int)] -> B.ByteString
scanline dat = B.pack (0 : (map fromIntegral $ concatMap (\(r,g,b) -> [r,g,b]) dat))
 
bitpack' :: [Bool] -> Word8 -> Word8 -> B.ByteString
bitpack' [] n b = if b /= 0x80 then B.singleton n else B.empty
bitpack' (x:xs) n b =
    if b == 1
        then v `B.cons` bitpack' xs 0 0x80
        else bitpack' xs v (b `shiftR` 1)
    where v = if x then n else n .|. b
 
bitpack :: [Bool] -> B.ByteString
bitpack xs = bitpack' xs 0 0x80
 
crc :: B.ByteString -> Word32
crc xs = updateCrc 0xffffffff xs `xor` 0xffffffff
 
updateCrc :: Word32 -> B.ByteString -> Word32
updateCrc = B.foldl' crcStep
 
crcStep :: Word32 -> Word8 -> Word32
crcStep crc ch = (crcTab ! n) `xor` (crc `shiftR` 8)
    where n = fromIntegral (crc `xor` fromIntegral ch)
 
crcTab :: Array Word8 Word32
crcTab = listArray (0,255) $ flip map [0..255] (\n ->
    foldl' (\c k -> if c .&. 1 == 1
                      then 0xedb88320 `xor` (c `shiftR` 1)
                      else c `shiftR` 1) n [0..7])
