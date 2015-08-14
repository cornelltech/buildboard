package lcs

import "bytes"

func index(s string, i int) string {
	return string(s[i-1])
}

func max(a, b int) int {
	if a > b {
		return a
	} else {
		return b
	}
}

func lcs_len(a, b string) ([][]int, int) {
	arr := make([][]int, len(a)+1) //allow for the 0 prefix
	for i := 0; i < len(arr); i++ {
		arr[i] = make([]int, len(b)+1) //allow for the 0 prefix
	}
	//
	for i := 1; i < len(a)+1; i++ {
		for j := 1; j < len(b)+1; j++ {
			if index(a, i) == index(b, j) {
				arr[i][j] = arr[i-1][j-1] + 1
			} else {
				arr[i][j] = max(arr[i-1][j], arr[i][j-1])
			}
		}
	}
	return arr, arr[len(a)][len(b)]

}

func Diff(a, b string) string {
	arr, _ := lcs_len(a, b)
	var buf bytes.Buffer
	var helper func(int, int)
	helper = func(i, j int) {
		if i > 0 && j > 0 && index(a, i) == index(b, j) {
			helper(i-1, j-1)
			buf.WriteString(" " + index(a, i))
		} else if j > 0 && (i == 0 || arr[i][j-1] >= arr[i-1][j]) {
			helper(i, j-1)
			buf.WriteString("+ " + index(b, j))
		} else if i > 0 && (j == 0 || arr[i][j-1] < arr[i-1][j]) {
			helper(i-1, j)
			buf.WriteString("- " + index(a, i))
		} else {
			buf.WriteString("")
		}
	}
	helper(len(a), len(b))
	return buf.String()
}
