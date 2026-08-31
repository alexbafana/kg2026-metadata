import plaintext_detail
import detail_entity.detail_entity
import emtak_faiss.emtak_faiss
import rdf.rdf

print("plaintext to detail")
plaintext_detail.main()
print("detail to entity")
#detail_entity.detail_entity.main() #needs openai key
print("emtak faiss codes")
emtak_faiss.emtak_faiss.main()
print("rdf ttl files")
rdf.rdf.main()