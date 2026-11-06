# Overlap proportions for six network measures.
library(reshape2)
library(ggplot2)
library(jsonlite)

plot_overlap <- function(network) {
  config_path <- Sys.getenv("RESEARCH_CONFIG", "config.json")
  config <- fromJSON(config_path)
  directory <- Sys.getenv("RESEARCH_DATA_DIR", config$data_dir)
  if (!grepl("^(/|[A-Za-z]:)", directory)) directory <- file.path(dirname(config_path), directory)
  path <- file.path(directory, paste0(network, "_overlap.csv"))
  df <- read.csv(path, header=TRUE, check.names=FALSE, encoding="UTF-8")
  if (ncol(df) != 7) stop("Expected a row-label column and six overlap columns")
  names(df) <- c("X", "D", "2stepD", "CD", "degree", "h", "pagerank")
  measures <- c("D", "2stepD", "CD", "degree", "h", "pagerank")
  if (any(!df$X %in% measures)) stop("Unknown overlap row labels")
  df$X <- factor(df$X, levels=measures)
  long <- melt(df, id.vars="X", variable.name="variable", value.name="value")
  if (any(!is.finite(long$value)) || any(long$value < 0 | long$value > 1)) stop("Overlap values must be finite proportions in [0, 1]")
  long$value <- round(long$value * 100, 2)
  p <- ggplot(long, aes(x=variable, y=X, size=value, alpha=value)) +
    geom_point(color="#1B4F72", shape=18) +
    geom_text(aes(label=paste0(value, "%")), size=4.5) +
    scale_size_continuous(range=c(15, 30)) +
    scale_alpha_continuous(range=c(0.5, 1)) +
    theme_bw() + theme(legend.position="none", axis.text=element_text(size=14)) +
    labs(x=NULL, y=NULL) + coord_fixed()
  output <- Sys.getenv("RESEARCH_OUTPUT_DIR", config$output_dir)
  if (!grepl("^(/|[A-Za-z]:)", output)) output <- file.path(dirname(config_path), output)
  dir.create(output, recursive=TRUE, showWarnings=FALSE)
  ggsave(file.path(output, paste0(network, "_overlap.pdf")), plot=p, width=9, height=9)
  print(p)
}
