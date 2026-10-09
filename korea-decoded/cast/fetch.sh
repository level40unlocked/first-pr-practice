#!/bin/sh
# Rig source images (head / body / ref) for the whole cast. Higgsfield jobs are listed in docs/show_bible.md.
# Not kept in git: run this once per checkout.
cd "$(dirname "$0")"
B=https://d8j0ntlcm91z4.cloudfront.net/user_3EqGMSR4UWAmjj632i5YewaH0hU
get() { [ -f "$1" ] || curl -sSf -o "$1" "$B/$2"; }
get k_head.png hf_20260928_074351_497d2899-66fc-40ea-8b60-1d4815c18eb6.png
get k_body.png hf_20260928_074350_480e7f2e-bde1-49fe-ad18-dfc5d2599626.png
get k_ref.png hf_20260928_074351_5d746f9a-6b07-4adb-9eec-3936cf68fecf.png
get kangfree_head.png hf_20260928_084541_c67fcd43-9c73-473c-b29f-4be8a1cd81e5.png
get kangfree_body.png hf_20260928_084541_ec8bd826-58a3-4d75-bff3-18cce3c5a521.png
get kangfree_ref.png hf_20260928_084541_2a93c3aa-974e-40fb-b63a-26662d2f9796.png
get joe_head.png hf_20260928_165107_c5e59c4d-2984-453a-91ca-ccf2153ac3b4.png
get joe_body.png hf_20260928_165106_2fa7ec12-1a53-4cb8-bd68-810fb8ddb92b.png
get joe_ref.png hf_20260928_165107_7d92559c-197b-48c5-8466-b9bda1657d77.png
get news_head.png hf_20260928_172010_98ee6a07-7734-4753-96e6-0b5a91fde7f6.png
get news_body.png hf_20260928_171717_54cc1983-d650-4b56-a2e3-90463392b6fd.png
get news_ref.png hf_20260928_171718_8d457ae0-b9ec-4ace-9d67-ec5b28ae22d2.png
get kpop_head.png hf_20260928_172010_d4b4123a-4902-4444-bfdf-8765f698db2d.png
get kpop_body.png hf_20260928_171719_f3663c92-2286-4259-bfab-6e1f6805358e.png
get kpop_ref.png hf_20260928_171717_4cffa2cb-d2e4-4ddd-833c-0797fdb0dcdb.png
get hidden_head.png hf_20260928_171717_e1cc0cfa-b1c4-4ac3-a9c4-ef07c7d09d49.png
get hidden_body.png hf_20260928_171717_a7ab925d-7875-472e-b1eb-7c393c5fb22e.png
get hidden_ref.png hf_20260928_171717_d3176932-0ab2-4cff-9de7-194e23534230.png
get money_head.png hf_20260928_171717_26dfccdd-4424-4ea7-825c-ed2c250642dc.png
get money_body.png hf_20260928_171717_94549376-7493-4a34-a337-93751110c81e.png
get money_ref.png hf_20260928_171717_74bdfdab-b788-4cc4-b816-ac961492bd97.png
get tech_head.png hf_20260928_171816_e03fc864-ae7f-4f00-a0cf-bd654a896fba.png
get tech_body.png hf_20260928_171816_318c95ef-dae2-4a30-977e-f5a4b2f1f8ab.png
get tech_ref.png hf_20260928_171816_cea28273-31a5-4b36-b0d5-3dac4b1ebcdf.png
get chef_head.png hf_20260928_171816_0bd12c40-1b8c-4b10-a8eb-5cfd71abb7a1.png
get chef_body.png hf_20260928_171816_8f82a8f8-16f4-4463-81c1-dc2a894701b9.png
get chef_ref.png hf_20260928_171817_fb596434-ab49-4e73-94fd-962ea517bfad.png
get travel_head.png hf_20260928_171816_ba5318d0-494b-4d31-b8ba-bf2f109d7cf6.png
get travel_body.png hf_20260928_171849_209a0f95-d747-44fb-b7c3-1fd811e83c7d.png
get travel_ref.png hf_20260928_171816_94e6999f-cd85-4a0b-ac2b-818200c55a79.png
