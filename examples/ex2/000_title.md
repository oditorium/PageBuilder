// When multiple files are joined, the individual meta data
// fields are joined to create the meta data for the final
// file. Importantly this happens in reverse order, ie the
// definition is taken where it was _first_ defined and
// can not be overwritten. It is therefore convenient to
// create a `000_title.md` file that only contains the title,
// as well as all the meta data used for the joined file

// The tags recognised are mostly the same as for the
// individual files. additionally there are two new tags:
// `join` and `jointfilename`. If one of the former is present,
// joint output is always generated (this avoids using the
// *--join* flag on the command line). The latter determines
// the name of the joint file (default is `document.html`)


:title:             Example 2               
:tags:              test, test1
:keywords:          test, metamarkdown
:headinglevel:      0
:meta:              field1 := value1, field2 := value2
:join:              1
:jointfilename:     document.html

# The Overall Title
