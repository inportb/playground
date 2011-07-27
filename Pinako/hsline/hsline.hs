module Main where

{- Examples:
	echo:
		cat hsline.hs | ./hsline
		cat hsline.hs | ./hsline '\s -> Right s'
	strip leading and trailing whitespace, and collapse contiguous whitespace:
		cat hsline.hs | ./hsline '\s -> Right (unwords (words s))'
	filter lines with more than 50 characters
		cat hsline.hs | ./hsline '\s -> if length s > 50 then Right s else Left ()'
	reverse lines with more than 50 characters
		cat hsline.hs | ./hsline '\s -> if length s > 50 then Right (reverse s) else Right s'
	filter first word of each line (using words)
		cat hsline.hs | ./hsline '\s -> do { let { w = (words s) }; if length w > 0 then Right (head (words s)) else Left () }'
	filter first word of each line (using Data.List.Split.splitOn)
		cat hsline.hs | ./hsline -mData.List.Split '\s -> Right (head (splitOn " " s))'
	grep
		cat hsline.hs | ./hsline -mText.Regex.TDFA '\s -> if a =~ "import"::Bool then Right s else Left ()'
	sed
		cat hsline.hs | ./hsline -mText.Regex '\s -> Right (subRegex (mkRegex "\\[(.*)\\]") s "{\\1}")'
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
		(_,_,errs)	-> fail (concat errs ++ usageInfo "Usage: hsline [line expression ...]" options)

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
