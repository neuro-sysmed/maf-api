CREATE TABLE meta (
  id             UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,

  name           VARCHAR(80) NOT NULL,
  value          VARCHAR(80) NOT NULL
);

CREATE TABLE project (
  id    UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  name  VARCHAR(80) UNIQUE,
  description TEXT,
  sample_count INT DEFAULT 0
);

CREATE TABLE variant (
  id    UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,

  chrom            VARCHAR(80) NOT NULL,
  pos 		         INT NOT NULL,
  ref              VARCHAR(1000) NOT NULL,
  alt              VARCHAR(1000) NOT NULL,

  allele_number    INT,
  allele_count     INT,
  allele_count_hom INT,
  frequency        FLOAT

);

CREATE INDEX variant_var_idx ON variant (chrom, pos, ref, alt);
CREATE INDEX variant_pos_idx ON variant (chrom, pos);

CREATE TABLE project_variant (

  id    UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  project_id         UUID references project(id),
  variant_id         UUID references variant(id),

  allele_number  INT DEFAULT 0,
  allele_count   INT DEFAULT 0,
  allele_count_hom INT DEFAULT 0,
  frequency      FLOAT DEFAULT 0

);

CREATE INDEX project_variant_proj_idx ON project_variant(project_id);
CREATE INDEX project_variant_var_idx ON project_variant(variant_id);

CREATE TABLE gene (
  id              UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,

  name		      VARCHAR(80),
  transcript      VARCHAR(200)
);

CREATE INDEX gene_name_idx ON gene(name);
CREATE INDEX gene_trans_idx ON gene(transcript);

CREATE TABLE variant_annotation (

  id          UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  gene_id     UUID references gene(id),
  variant_id  UUID references variant(id),  


  transcript VARCHAR(80),
  canonical  BOOLEAN,
  effect     VARCHAR(80),
  npos       VARCHAR(80),
  cpos	     VARCHAR(80),
  DNA_change VARCHAR(80),
  AA_change  VARCHAR(80),
  polyphen   VARCHAR(80),
  sift       VARCHAR(80),

  dbsnp      VARCHAR(80),
  gnomad     VARCHAR(80)
  
);

CREATE INDEX var_annot_gene_idx ON variant_annotation(gene_id);
CREATE INDEX var_annot_var_idx ON variant_annotation(variant_id);

CREATE TABLE region (

  id       UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  chrom                 VARCHAR(8) NOT NULL ,
  region_start               INT NOT NULL,
  region_end                 INT NOT NULL
);

CREATE INDEX region_idx ON region(chrom, region_start, region_end);


CREATE TABLE gene_exon (
  id       UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  gene_id         UUID references gene(id),
  region_id         UUID references region(id),

  exon_nr   INT
);

CREATE INDEX gene_exon_idx ON gene_exon(gene_id, region_id);





