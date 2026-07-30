from hotglue_smoke_test.vcr.tap import VCRTapTestRunner

class AirbaseTestRunner(VCRTapTestRunner):

    def module(self) -> str:
        return "tap_hotglue"

    def launch(self):
        from tap_hotglue.tap import TapHotglue
        TapHotglue.cli()


if __name__ == "__main__":
    AirbaseTestRunner.main()