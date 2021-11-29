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
            v['frequencies'] = self.project_afs(v['id'])
            return v

        return None

    def variant_get_by_id(self, id:str) -> dict:
        v = self._db.get_by_id('variant', value=id)

        if v is not None and v != []:
            v = v[0]
            v['frequencies'] = self.project_afs(v['id'])
            print( v )
            return v

        return None

    def variant_add(self, chrom:str, pos:int, ref:str, alt:str) -> str:

        v = self._db.get('variant', chrom=chrom, pos=pos, ref=ref, alt=alt)
#        print( f"v (va) {v}" )
        
        if v is not None and v != []:
#            print( 'returning id...')
            return v[0]['id']

#        print('adding variant')
        p = self._db.add('variant', {'chrom': chrom, 'pos': pos, 'ref':ref, 'alt':alt})

#        print( "getting variant...")
        v = self._db.get('variant', chrom=chrom, pos=pos, ref=ref, alt=alt)
#        print( f"v (va2) {v}" )
        return v[0]['id']


    def project_variant_add(self, project_id:str, variant_id:str, allele_number:int, allele_count:int,  allele_count_hom:int, frequency:float) -> str:
        v = self._db.get('project_variant', project_id=project_id, variant_id=variant_id)
        if v is not None and v != []:
            v = v[0]
            id = v['id']
            if v['frequency'] == frequency:
#                print('already stored')
                return
#            print('update MAF')
            v = {'allele_number': allele_number, 'allele_count': allele_count, 
                 'allele_count_hom': allele_count_hom, 'frequency':frequency}
            self._db.update('project_variant', v, {'id': id})
#            return v['id']
        else:
#            print('adding AF')
            v = self._db.add('project_variant', {'project_id': project_id, 'variant_id': variant_id, 
                                             'allele_number': allele_number, 'allele_count': allele_count, 
                                             'allele_count_hom': allele_count_hom, 'frequency':frequency})
#            return v[0]['id']



    def project_variant(self, project_id:str, variant_id:str) -> dict:
        v = self._db.get_single('project_variant', project_id=project_id, variant_id=variant_id)
        return v


    def variants_in_region(self, chrom:str, start:int=None, end:int=None) -> list:
        q = f"SELECT * FROM variant WHERE chrom='{chrom}' "

        if start is not None:
            q += f" AND pos >= {start}"

        if end is not None:
            q += f" AND pos <= {end}"


#        print( f"Q :: {q}  order by chrom,pos;" )
        vars = self._db.get_as_dict(f"{q} order by chrom,pos;")
        return vars


    def project_afs(self, variant_id:str) -> list:
        mfs = self._db.get('project_variant', variant_id=variant_id)
        for mf in mfs:
            project = self.projects(id=mf['project_id'])
            mf['project_name'] = project[0]['name']
            del mf['variant_id']
            del mf['id']
        return mfs

