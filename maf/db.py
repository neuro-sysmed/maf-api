import kbr.db_utils as db


class DB(object):

    def connect(self, url: str) -> None:
        self._db = db.DB(url)

    def disconnect(self) -> None:

        if self._db is not None:
            self._db.close()

    def projects(self, **values) -> dict:
        return self._db.get('project', **values)


    def project_create(self, name:str) -> dict:
        return self._db.add_unique('project', {'name': name}, 'name')

    def project_update(self, values: dict) -> dict:
        self._db.update('project', values, {'id': values['id']})

    def project_delete(self, id) -> dict:
        self._db.delete('project', id=id)

    def variants(self, **values) -> dict:
        return self._db.get('variant', **values)

    def variant_get(self, chrom:str, pos:int, ref:str, alt:str) -> dict:
        v = self._db.get('variant', chrom=chrom, pos=pos, ref=ref, alt=alt)

        if v is not None and v != []:
            v = v[0]
            v['mafs'] = self.mafs(v['id'])
            return v

        return None

    def variant_get_by_id(self, id:str) -> dict:
        v = self._db.get_by_id('variant', value=id)

        if v is not None and v != []:
            v = v[0]
            v['mafs'] = self.mafs(v['id'])
            print( v )
            return v

        return None

    def variant_add(self, chrom:str, pos:int, ref:str, alt:str) -> str:

        v = self._db.get('variant', chrom=chrom, pos=pos, ref=ref, alt=alt)
        #print( v )
        
        if v is not None and v != []:
            return v[0]['id']

        self._db.add('variant', {'chrom': chrom, 'pos': pos, 'ref':ref, 'alt':alt})
        v = self._db.get('variant', chrom=chrom, pos=pos, ref=ref, alt=alt)
        return v[0]['id']


    def project_variant_add(self, project_id:str, variant_id:str, maf:float, coverage:int=0, alt_alleles:int=0) -> str:
        v = self._db.get('project_variant', project_id=project_id, variant_id=variant_id)
        if v is not None and v != []:
            v = v[0]
            if v['maf'] == maf:
#                print('already stored')
                return
#            print('update MAF')
            v['maf'] = maf
            self._db.update('project_variant', v, {'id':id})
        else:
#            print('create MAF')
            self._db.add('project_variant', {'project_id': project_id, 'variant_id': variant_id, 
                                             'maf':maf, 'coverage':coverage, 'alt_alleles': alt_alleles})


    def region_get(self, chrom:str, start:int, end:int) -> list:
        q = f"SELECT * FROM VARIANT WHERE chrom='{chrom}' and pos>={start} and pos<={end};"

        vars = self._db.get_as_dict(q)
        for var in vars:
            var['mafs'] = self.mafs(var['id'])
        return vars


    def mafs(self, variant_id:str) -> list:
        mfs = self._db.get('project_variant', variant_id=variant_id)
        for mf in mfs:
            del mf['variant_id']
            del mf['id']
        return mfs

