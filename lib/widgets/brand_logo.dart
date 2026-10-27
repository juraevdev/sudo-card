import 'package:flutter/material.dart';

/// UzNext lockup: "UN" mark followed by the "UzNext" wordmark.
/// [size] is the height of the mark.
class BrandLogo extends StatelessWidget {
  const BrandLogo({super.key, this.size = 24});

  final double size;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Image.asset(
          'assets/brand/uznext_mark.png',
          height: size,
          filterQuality: FilterQuality.medium,
        ),
        SizedBox(width: size * 0.3),
        Image.asset(
          'assets/brand/uznext_wordmark.png',
          height: size * 0.5,
          filterQuality: FilterQuality.medium,
        ),
      ],
    );
  }
}
