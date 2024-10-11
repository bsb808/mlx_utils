# mlx_utils

## mlx_remove_code

Replace the content of code blocks in MATLAB live script mlx-files with `% Your code here.`

The is useful for creating assignments.  The instructor creates a live script with the solution, e.g. `assignment_soln.mlx`.  The program processes the mlx file, [MATLAB live code format](https://www.mathworks.com/help/matlab/matlab_prog/live-script-file-format.html), by expanding the MLX archive and reading the `document.xml` file.  We replace the contents of the code blocks with a single comment line and then compress the archive into a new `assignment.mlx` file so that the assignment includes all the instructions, but not the code solutions.
