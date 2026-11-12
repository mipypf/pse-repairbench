# PSE-RepairBench v0.1 契約仕様

## 研究スコープ

PSE-RepairBench v0.1 は executable semantic repair を評価する。対象は、
faulty な DWSIM flowsheet が simulator 上で正常に load/solve できる一方で、
既存 process object の scalar な configuration、operating、または
specification parameter が不適切なため、process target を満たさないケースである。

この benchmark は、GUI レベルの破損、壊れたファイル、欠落した topology を主対象にしない。
モデルが process observation を読み取り、工学的に意味のある parameter intervention を選び、
canonical repair JSON を出力し、実行可能な DWSIM rerun によって target を回復できるかを測る。

## v0.1 で固定する契約

- instance は `instances/<split>/<instance_id>/instance.json` に置き、manifest 内の path はすべて instance directory からの相対 path とする。
- `public/` には model-visible artifact のみを置く。`hidden/` には gold action、exact-gold mock fixture、base/repaired flowsheet、run artifact、metrics report を置く。
- release validation は `public/**` 全体を scan し、hidden path、exact gold、base value、fault label、legacy action の leakage を検出する。
- 評価順序は schema validation、executor application、DWSIM rerun、executable target-success check、gold-proximity scoring とする。
- 主指標は executable target success とする。gold proximity は副次的な diagnostic metric として扱う。

## Canonical Repair Output

モデルは `diagnosis`、`repair_actions`、top-level `rationale` を持つ単一の repair-output JSON object を返す。

各 repair action は canonical な `set_unit_parameter` action とする。

```json
{
  "type": "set_unit_parameter",
  "target": {
    "kind": "unit_operation",
    "guid": "DC-84eedf9c-acf3-4dfc-8675-2245dc73de75",
    "tag": "DC-01"
  },
  "parameter": {
    "namespace": "column_specification",
    "name": "reflux_ratio"
  },
  "value": 7.50199999999571,
  "unit": null,
  "rationale": "optional action-level rationale"
}
```

`target.kind` は必須とする。初期 release-supported kind は `unit_operation` である。
`material_stream` は v0.2 の feed-condition repair に向けた拡張点として予定するが、
v0.1 では release-supported ではない。

reaction/conversion 系の修正は `target.kind: "unit_operation"` の将来 parameter family として扱う。
v0.1 では release-supported ではないが、`reactor_condition/temperature`、
`reactor_specification/conversion`、`reactor_condition/residence_time` を planned unit-operation
parameter family として残す。

action-level の `rationale` は optional とする。top-level の `rationale` は必須のままにし、
executable action は compact に保ちつつ、model reasoning は記録できるようにする。

## Support Level Registry

この registry は、v0.1 contract で名前を予約する target kind と parameter family の範囲を示す。
`release-supported` は schema、executor、release validator、evaluator で実行確認する対象である。
`provisional` は contract 上の候補として保持するが、release-supported ではない対象である。
`planned` は v0.2 以降の拡張候補であり、v0.1 schema/executor の対応を意味しない。

| support level | target kind | parameter |
| --- | --- | --- |
| release-supported | `unit_operation` | `column_specification/reflux_ratio` |
| release-supported | `unit_operation` | `column_configuration/feed_stage` |
| planned | `unit_operation` | `reactor_specification/conversion` |
| planned | `unit_operation` | `reactor_condition/temperature` |
| planned | `unit_operation` | `reactor_condition/residence_time` |
| planned | `material_stream` | `stream_condition/temperature` |
| planned | `material_stream` | `stream_condition/pressure` |
| planned | `material_stream` | `stream_condition/flowrate` |
| planned | `material_stream` | `stream_composition/mole_fraction` |

## Support Summary

| 契約領域 | v0.1 での扱い |
| --- | --- |
| Research task | 固定: scalar process-object parameter fault に対する executable semantic repair |
| Target kind | Release-supported: `unit_operation`; v0.2 planned feed-condition extension: `material_stream` |
| Action type | 固定: `set_unit_parameter` |
| 現在の release parameter | `column_specification/reflux_ratio`, `column_configuration/feed_stage` |
| planned unit-operation parameter family | `reactor_specification/conversion`, `reactor_condition/temperature`, `reactor_condition/residence_time` |
| planned material-stream parameter family | `stream_condition/temperature`, `stream_condition/pressure`, `stream_condition/flowrate`, `stream_composition/mole_fraction` |
| executor support | `unit_operation` + `column_specification/reflux_ratio` / `column_configuration/feed_stage` |
| release validator support | 現在の distillation reflux-ratio seed と feed-stage seed |
| evaluator report fields | `schema`, `action_schema`, `executor`, `dwsim`, `target_metric`, `success_criteria`, `executable_success`, `gold_proximity` |
| gold proximity fields | `target_match`, `parameter_match`, `unit_match`, `value_abs_error`, `value_rel_error` |

## v0.2 拡張点

- feed temperature、pressure、flowrate、composition repair のために `target.kind: "material_stream"` を追加する。
- unit operation と stream condition 向けの scalar parameter namespace を追加する。
- reactor temperature、conversion、residence time などの reaction/conversion family を unit operation repair として追加する。
- executor が対応する parameter family を support した後、release validation を現在の reflux-ratio seed 以外にも一般化する。
- scalar executable semantic repair が安定した後、property-package/model-choice repair を追加する。
