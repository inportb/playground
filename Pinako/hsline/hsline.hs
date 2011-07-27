module Main where

{- Examples:
	echo:
		cat hsline.hs | ./hsline
	strip leading and trailing whitespace, and collapse contiguous whitespace:
		cat hsline.hs | ./hsline '\a -> Right (unwords (words a))'
	strip spaces, with helper function:
		cat hsline.hs | ./hsline 'strip s -> (unwords (words a))' '\a -> Right (unwords (words a))'
	filter lines with more than 50 characters
		cat hsline.hs | ./hsline '\a -> if length a > 50 then Right a else Left ()'
	reverse lines with more than 50 characters
		cat hsline.hs | ./hsline '\a -> if length a > 50 then Right (reverse a) else Right a'
	filter first word of each line (using words)
		cat hsline.hs | ./hsline '\line -> do { let { w = (words line) }; if length w > 0 then Right (head (words line)) else Left () }'
	filter first word of each line (using Data.List.Split.splitOn)
		cat hsline.hs | ./hsline -mData.List.Split '\line -> Right (head (splitOn " " line))'
	grep
		cat hsline.hs | ./hsline -mText.Regex.TDFA '\a -> if a =~ "import"::Bool then Right a else Left ()'
	sed
		cat hsline.hs | ./hsline -mText.Regex '\a -> Right (subRegex (mkRegex "\\[(.*)\\]") a "{\\1}")'
-}

import System.Environment (getArgs)
import System.Console.GetOpt
import System.Exit
import Data.List (unwords,nub)
import Data.List.Split (splitOn)
--import Text.Regex.TDFA
import Language.Haskell.Interpreter (setImports, eval, interpret, as, runInterpreter, Interpreter)
import IO

data Flags = Flags
	{ verbose	:: Bool
	, modules	:: String
	} deriving Show

options :: [OptDescr (Flags -> Flags)]
options =
	[ Option ['v']		["verbose"]	(NoArg verbose)
		"be chatty"
	, Option ['m']		["modules"]	(ReqArg modules "module1,module2,...")
		"import modules"
	] where
		verbose f  = f { verbose = True }
		modules m f = f { modules = m }

parseOptions :: [String] -> IO (Flags, [String])
parseOptions argv =
	case getOpt RequireOrder options argv of
		(o,n,[])	-> return ((foldr (\f r -> f r) (Flags False "") o), n)
		(_,_,errs)	-> fail (concat errs ++ usageInfo "Usage: hsline [setup expression] [line expression ...]" options)

main = do
	opts <- getArgs
	(flags,extra) <- parseOptions opts
	let expr = if (length extra) > 0
		then unwords extra
		else "\\line -> Right line"
{-
	let setup = if (length extra) > 1
		then head extra
		else "()"
	let expr = case (length extra) of
		0	-> "\\line -> Right line"
		1	-> head extra
		_	-> unwords (tail extra)
-}
	let m = modules flags
	let imports = if (length m) > 0
		then splitOn "," m
		else []
{-
	let truncate s = (take ((length s)-1)) s
	let imports = "Prelude":(map truncate (nub (map head (expr =~ "[[:alpha:]_][[:alnum:]\\.]*\\." :: [[String]]))))
-}
	let resIO = setImports (nub ("Prelude":imports)) >> interpret expr (as :: String -> (Either () String)) :: Interpreter (String -> (Either () String))
	res <- runInterpreter resIO
	case res of
		Left err -> hPutStrLn stderr (show err)
		Right fn ->
			stdinloop fn

stdinloop :: (String -> (Either () String)) -> IO ()
stdinloop f = do
	end <- isEOF
	if end
		then exitWith ExitSuccess
		else do
			line <- hGetLine stdin
			case f line of
				Left r	-> putStr ""
				Right r	-> putStrLn r
			stdinloop f
