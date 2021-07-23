CREATE TABLE project (
  id    UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  name  VARCHAR(80) UNIQUE
);


CREATE TABLE variant (
  id    UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,

  chr             VARCHAR(8) NOT NULL ,
  pos 		      INT NOT NULL,
  ref             VARCHAR(100) NOT NULL ,
  alt             VARCHAR(100) NOT NULL ,

);

CREATE INDEX variant_var_idx ON variant (chr, pos, ref, alt);
CREATE INDEX variant_pos_idx ON variant (chr, pos);

CREATE TABLE project_variant (

  id    UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  project_id         UUID references project(id),
  variant_id         UUID references variant(id),

  MAF		         FLOAT,	  
  quality	         FLOAT,  
  allele_count	     INT NOT NULL,


  PRIMARY KEY idx  (sid, vid),
  KEY sid_idx  (sid),
  KEY vid_idx  (vid)
);

CREATE INDEX project_variant_proj_idx ON project_variant(project_id);
CREATE INDEX project_variant_var_idx ON project_variant(variant_id);

CREATE TABLE gene (
  id              UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,

  name		      VARCHAR(80),
  transcript      VARCHAR(200),

  KEY name_idx (name)
);

CREATE INDEX gene_name_idx ON gene(name);
CREATE INDEX gene_trans_idx ON gene(transcript);


CREATE TABLE variant_annotation (

  id       UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  gene_id         UUID references gene(id),
  variant_id         UUID references variant(id),  


  dbsnp      VARCHAR(80),
  effect     VARCHAR(80),
  npos       VARCHAR(80),
  cpos	     VARCHAR(80),
  DNA_change VARCHAR(80),
  AA_change  VARCHAR(80),
  polyphen   VARCHAR(80),
  sift       VARCHAR(80),


  KEY gid_idx (gid),
  KEY vid_idx (vid)
);

CREATE INDEX var_annot_gene_idx ON variant_annotation(gene_id);
CREATE INDEX var_annot_var_idx ON variant_annotation(variant_id);

CREATE TABLE region (

  id       UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  chr                 VARCHAR(8) NOT NULL ,
  start               INT NOT NULL,
  end                 INT NOT NULL,

  KEY pos_idx  (chr, start, end)
);

CREATE INDEX region_idx ON region(chr, start, end);


CREATE TABLE gene_exon (
  id       UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  gene_id         UUID references gene(id),
  region_id         UUID references region(id),

  exon_nr   INT,

 PRIMARY KEY idx (rid, gid)
);

CREATE INDEX gene_exon_idx ON gene_exon(gene_id, region_id);





