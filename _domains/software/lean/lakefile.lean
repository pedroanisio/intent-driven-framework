import Lake
open Lake DSL

package intentFramework where
  leanOptions := #[
    ⟨`autoImplicit, false⟩
  ]

@[default_target]
lean_lib IntentFramework where
  srcDir := "."
