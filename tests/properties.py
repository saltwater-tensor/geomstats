"""Test properties of differential geometry."""

import geomstats.backend as gs


def _is_isometry(
    metric,
    space,
    tangent_vec,
    trans_tangent_vec,
    base_point,
    is_tangent_atol,
    rtol,
    atol,
):
    """Check that a transformation is an isometry.

    This is an auxiliary function.

    Parameters
    ----------
    metric : RiemannianMetric
        Riemannian metric.
    tangent_vec : array-like
        Tangent vector at base point.
    trans_tangent_vec : array-like
        Transformed tangent vector at base point.
    base_point : array-like
        Point on manifold.
    is_tangent_atol: float
        Asbolute tolerance for the is_tangent function.
    rtol : float
        Relative tolerance to test this property.
    atol : float
        Absolute tolerance to test this property.
    """
    is_tangent = space.is_tangent(trans_tangent_vec, base_point, is_tangent_atol)
    is_equinormal = gs.isclose(
        metric.norm(trans_tangent_vec, base_point),
        metric.norm(tangent_vec, base_point),
        rtol,
        atol,
    )
    return gs.logical_and(is_tangent, is_equinormal)


class ManifoldProperties:
    def belongs_shape(self, space_args, point, expected):
        """Check that belongs returns an array of the expected shape.

        Parameters
        ----------
        space_args : tuple
            Arguments to pass to constructor of the manifold.
        point : array-like
            Point.
        expected : tuple
            Expected shape for the result of the belongs function.
        """
        space = self.space(*space_args)
        result = gs.shape(space.belongs(gs.array(point)))
        self.assertAllClose(result, expected)

    def to_tangent_shape(self, space_args, vector, expected):
        """Check that to_tangent returns an array of the expected shape.

        Parameters
        ----------
        space_args : tuple
            Arguments to pass to constructor of the manifold.
        point : array-like
            Point.
        expected : tuple
            Expected shape for the result of the belongs function.
        """
        space = self.space(*space_args)
        result = gs.shape(space.to_tangent(gs.array(vector)))
        self.assertAllClose(result, expected)

    def projection_belongs(self, space_args, point, belongs_atol):
        """Check that a point projected on a manifold belongs to the manifold.

        Parameters
        ----------
        space_args : tuple
            Arguments to pass to constructor of the manifold.
        point : array-like
            Point to be projected on the manifold.
        belongs_atol : float
            Absolute tolerance for the belongs function.
        """
        space = self.space(*space_args)
        belongs = space.belongs(space.projection(gs.array(point)), belongs_atol)
        self.assertAllClose(gs.all(belongs), gs.array(True))

    def to_tangent_is_tangent(self, space_args, vector, base_point, is_tangent_atol):
        """Check that to_tangent returns a tangent vector.

        Parameters
        ----------
        space_args : tuple
            Arguments to pass to constructor of the manifold.
        vector : array-like
            Vector to be projected on the tangent space at base_point.
        base_point : array-like
            Point on the manifold.
        is_tangent_atol : float
            Absolute tolerance for the is_tangent function.
        """
        space = self.space(*space_args)
        tangent = space.to_tangent(gs.array(vector))
        result = gs.all(space.is_tangent(tangent, base_point, is_tangent_atol))
        self.assertAllClose(result, gs.array(True))


class OpenSetProperties(ManifoldProperties):
    def to_tangent_belongs_ambient_space(self, space_args, data, belongs_atol):
        space = self.space(*space_args)
        result = gs.all(space.ambient_space.belongs(gs.array(data), belongs_atol))
        self.asertAllClose(result, gs.array(True))


class LieGroupProperties:
    def exp_log_composition(self, group_args, tangent_vec, base_point, rtol, atol):
        """Check that group exponential and logarithm are inverse.

        This is calling group exponential first, then group logarithm.

        Parameters
        ----------
        group_args : tuple
            Arguments to pass to constructor of the group.
        tangent_vec : array-like
            Tangent vector to the manifold at base_point.
        base_point : array-like
            Point on the manifold.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        group = self.group(*group_args)
        exp_point = group.exp_from_identity(gs.array(tangent_vec), gs.array(base_point))
        log_vec = group.log_from_identity(exp_point, gs.array(base_point))
        self.assertAllClose(log_vec, gs.array(tangent_vec), rtol, atol)

    def log_exp_composition(self, group_args, point, base_point, rtol, atol):
        """Check that group exponential and logarithm are inverse.

        This is calling group logarithm first, then group exponential.

        Parameters
        ----------
        group_args : tuple
            Arguments to pass to constructor of the group.
        point : array-like
            Point on the manifold.
        base_point : array-like
            Point on the manifold.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        group = self.group(*group_args)
        log_vec = group.log_from_identity(gs.array(point), gs.array(base_point))
        exp_point = group.exp_from_identity(log_vec, gs.array(base_point))
        self.assertAllClose(exp_point, gs.array(point), rtol, atol)


class VectorSpaceProperties:
    def basis_belongs(self, space_args, belongs_atol):
        """Check that basis elements belong to vector space.

        Parameters
        ----------
        space_args : tuple
            Arguments to pass to constructor of the vector space.
        belongs_atol : float
            Absolute tolerance of the belongs function.
        """
        space = self.space(*space_args)
        result = gs.all(space.belongs(space.basis, belongs_atol))
        self.assertAllClose(result, gs.array(True))

    def basis_cardinality(self, space_args):
        """Check that the number of basis elements is the dimension.

        Parameters
        ----------
        space_args : tuple
            Arguments to pass to constructor of the vector space.
        """
        space = self.space(*space_args)
        basis = space.basis
        self.assertAllClose(len(basis), space.dim)


class LieAlgebraProperties(VectorSpaceProperties):
    def basis_representation_matrix_representation_composition(
        self, algebra_args, matrix_rep, rtol, atol
    ):
        """Check that changing coordinate system twice gives back the point.

        A point written in basis representation is converted to matrix representation
        and back.

        Parameters
        ----------
        algebra_args : tuple
            Arguments to pass to constructor of the Lie algebra.
        matrix_rep : array-like
            Point on the Lie algebra given in its matrix representation.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        algebra = self.algebra(*algebra_args)
        basis_rep = algebra.basis_representation(gs.array(matrix_rep))
        result = algebra.matrix_representation(basis_rep)
        self.assertAllClose(result, gs.array(matrix_rep), rtol, atol)

    def matrix_representation_basis_representation_composition(
        self,
        algebra_args,
        basis_rep,
        rtol,
        atol,
    ):
        """Check that changing coordinate system twice gives back the point.

        A point written in matrix representation is converted to basis representation
        and back.

        Parameters
        ----------
        algebra_args : tuple
            Arguments to pass to constructor of the Lie algebra.
        basis_rep : array-like
            Point on the Lie algebra given in its basis representation.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        algebra = self.algebra(*algebra_args)
        mat_rep = algebra.matrix_representation(basis_rep)
        result = algebra.basis_representation(mat_rep)
        self.assertAllClose(result, gs.array(basis_rep), rtol, atol)


class LevelSetProperties(ManifoldProperties):
    def extrinsic_intrinsic_composition(self, space_args, point_extrinsic, rtol, atol):
        """Check that changing coordinate system twice gives back the point.

        A point written in extrinsic coordinates is converted to intrinsic coordinates
        and back.

        Parameters
        ----------
        space_args : tuple
            Arguments to pass to constructor of the manifold.
        point_extrinsic : array-like
            Point on the manifold in extrinsic coordinates.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        space = self.space(*space_args)
        point_intrinsic = space.extrinsic_to_intrinsic_coords(point_extrinsic)
        result = space.intrinsic_to_extrinsic_coords(point_intrinsic)
        expected = point_extrinsic

        self.assertAllClose(result, expected, rtol, atol)

    def intrinsic_extrinsic_composition(self, space_args, point_intrinsic, rtol, atol):
        """Check that changing coordinate system twice gives back the point.

        A point written in intrinsic coordinates is converted to extrinsic coordinates
        and back.

        Parameters
        ----------
        space_args : tuple
            Arguments to pass to constructor of the manifold.
        point_intrinsic : array-like
            Point on the manifold in intrinsic coordinates.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        space = self.space(*space_args)
        point_extrinsic = space.intrinsic_to_extrinsic_coords(point_intrinsic)
        result = space.extrinsic_to_intrinsic_coords(point_extrinsic)
        expected = point_intrinsic

        self.assertAllClose(result, expected, rtol, atol)


class ConnectionProperties:
    def exp_shape(self, connection_args, tangent_vec, base_point, expected):
        """Check that exp returns an array of the expected shape.

        Parameters
        ----------
        connection_args : tuple
            Arguments to pass to constructor of the connection.
        tangent_vec : array-like
            Tangent vector at base point.
        base_point : array-like
            Point on the manifold.
        expected : tuple
            Expected shape for the result of the exp function.
        """
        connection = self.connection(*connection_args)
        exp = connection.exp(gs.array(tangent_vec), gs.array(base_point))
        result = gs.shape(exp)
        self.assertAllClose(result, expected)

    def log_shape(self, connection_args, point, base_point, expected):
        """Check that log returns an array of the expected shape.

        Parameters
        ----------
        connection_args : tuple
            Arguments to pass to constructor of the connection.
        point : array-like
            Point on the manifold.
        base_point : array-like
            Point on the manifold.
        expected : tuple
            Expected shape for the result of the log function.
        """
        connection = self.connection(*connection_args)
        log = connection.log(gs.array(point), gs.array(base_point))
        result = gs.shape(log)
        self.assertAllClose(result, expected)

    def exp_belongs(
        self, connection_args, space, tangent_vec, base_point, belongs_atol
    ):
        """Check that the connection exponential gives a point on the manifold.

        Parameters
        ----------
        connection_args : tuple
            Arguments to pass to constructor of the connection.
        space : Manifold
            Manifold where connection is defined.
        tangent_vec : array-like
            Tangent vector at base point.
        base_point : array-like
            Point on the manifold.
        belongs_atol : float
            Absolute tolerance for the belongs function.
        """
        connection = self.connection(*connection_args)
        exp = connection.exp(gs.array(tangent_vec), gs.array(base_point))
        result = gs.all(space.belongs(exp, belongs_atol))
        self.assertAllClose(result, gs.array(True))

    def log_is_tangent(
        self, connection_args, space, base_point, point, is_tangent_atol
    ):
        """Check that the connection logarithm gives a tangent vector.

        Parameters
        ----------
        connection_args : tuple
            Arguments to pass to constructor of the connection.
        space : Manifold
            Manifold where connection is defined.
        base_point : array-like
            Point on the manifold.
        point : array-like
            Point on the manifold.
        is_tangent_atol : float
            Absolute tolerance for the is_tangent function.
        """
        connection = self.connection(*connection_args)
        log = connection.log(gs.array(base_point), gs.array(point))
        result = gs.all(space.is_tangent(log, gs.array(base_point), is_tangent_atol))
        self.assertAllClose(result, gs.array(True))

    def geodesic_ivp_belongs(
        self,
        connection_args,
        space,
        n_points,
        initial_point,
        initial_tangent_vec,
        belongs_atol,
    ):
        """Check that connection geodesics belong to manifold.

        This is for geodesics defined by the initial value problem (ivp).

        Parameters
        ----------
        connection_args : tuple
            Arguments to pass to constructor of the connection.
        space : Manifold
            Manifold where connection is defined.
        n_points : int
            Number of points on the geodesics.
        initial_point : array-like
            Point on the manifold.
        initial_tangent_vec : array-like
            Tangent vector at base point.
        belongs_atol : float
            Absolute tolerance for the belongs function.
        """
        connection = self.connection(*connection_args)
        geodesic = connection.geodesic(
            initial_point=initial_point, initial_tangent_vec=initial_tangent_vec
        )

        t = gs.linspace(start=0.0, stop=1.0, num=n_points)
        points = geodesic(t)

        result = space.belongs(points, belongs_atol)
        expected = gs.array(n_points * [True])

        self.assertAllClose(result, expected)

    def geodesic_bvp_belongs(
        self, connection_args, space, n_points, initial_point, end_point, belongs_atol
    ):
        """Check that connection geodesics belong to manifold.

        This is for geodesics defined by the boundary value problem (bvp).

        Parameters
        ----------
        connection_args : tuple
            Arguments to pass to constructor of the connection.
        space : Manifold
            Manifold where connection is defined.
        n_points : int
            Number of points on the geodesics.
        initial_point : array-like
            Point on the manifold.
        end_point : array-like
            Point on the manifold.
        belongs_atol : float
            Absolute tolerance for the belongs function.
        """
        connection = self.connection(*connection_args)

        geodesic = connection.geodesic(initial_point=initial_point, end_point=end_point)

        t = gs.linspace(start=0.0, stop=1.0, num=n_points)
        points = geodesic(t)

        result = space.belongs(points, belongs_atol)
        expected = gs.array(n_points * [True])

        self.assertAllClose(result, expected)

    def log_exp_composition(self, connection_args, point, base_point, rtol, atol):
        """Check that connection exponential and logarithm are inverse.

        This is calling connection logarithm first, then connection logarithm.

        Parameters
        ----------
        connection_args : tuple
            Arguments to pass to constructor of the connection.
        point : array-like
            Point on the manifold.
        base_point : array-like
            Point on the manifold.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        connection = self.connection(*connection_args)
        log = connection.log(gs.array(point), base_point=gs.array(base_point))
        result = connection.exp(tangent_vec=log, base_point=gs.array(base_point))
        self.assertAllClose(result, point, rtol=rtol, atol=atol)

    def exp_log_composition(self, connection_args, tangent_vec, base_point, rtol, atol):
        """Check that connection exponential and logarithm are inverse.

        This is calling connection exponential first, then connection logarithm.

        Parameters
        ----------
        connection_args : tuple
            Arguments to pass to constructor of the connection.
        tangent_vec : array-like
            Tangent vector to the manifold at base_point.
        base_point : array-like
            Point on the manifold.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        connection = self.connection(*connection_args)
        exp = connection.exp(tangent_vec=tangent_vec, base_point=gs.array(base_point))
        result = connection.log(exp, base_point=gs.array(base_point))
        self.assertAllClose(result, tangent_vec, rtol=rtol, atol=atol)

    def exp_ladder_parallel_transport(
        self,
        connection_args,
        direction,
        tangent_vec,
        base_point,
        scheme,
        n_rungs,
        alpha,
        rtol,
        atol,
    ):
        """Check that end point of ladder parallel transport matches exponential.

        Parameters
        ----------
        connection_args : tuple
            Arguments to pass to constructor of the connection.
        direction : array-like
            Tangent vector to the manifold at base_point.
        tangent_vec : array-like
            Tangent vector to the manifold at base_point.
        base_point : array-like
            Point on the manifold.
        scheme : str, {'pole', 'schild'}
            The scheme to use for the construction of the ladder at each step.
        n_rungs : int
            Number of steps of the ladder.
        alpha : float
            Exponent for the scaling of the vector to transport.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        connection = self.connection(*connection_args)

        ladder = connection.ladder_parallel_transport(
            tangent_vec,
            base_point,
            direction,
            n_rungs=n_rungs,
            scheme=scheme,
            alpha=alpha,
        )

        result = ladder["end_point"]
        expected = connection.exp(direction, base_point)

        self.assertAllClose(result, expected, rtol=rtol, atol=atol)

    def exp_geodesic_ivp(
        self, connection_args, n_points, tangent_vec, base_point, rtol, atol
    ):
        """Check that end point of geodesic matches exponential.

        Parameters
        ----------
        connection_args : tuple
            Arguments to pass to constructor of the connection.
        n_points : int
            Number of points on the geodesic.
        tangent_vec : array-like
            Tangent vector to the manifold at base_point.
        base_point : array-like
            Point on the manifold.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        connection = self.connection(*connection_args)
        geodesic = connection.geodesic(
            initial_point=base_point, initial_tangent_vec=tangent_vec
        )
        t = gs.linspace(start=0.0, stop=1.0, num=n_points)
        points = geodesic(t)
        result = points[:, -1]
        expected = connection.exp(tangent_vec, base_point)
        self.assertAllClose(expected, result, rtol=rtol, atol=atol)


class RiemannianMetricProperties(ConnectionProperties):
    def squared_dist_is_symmetric(self, metric_args, point_a, point_b, rtol, atol):
        """Check that the squared geodesic distance is symmetric.

        Parameters
        ----------
        metric_args : tuple
            Arguments to pass to constructor of the metric.
        point_a : array-like
            Point on the manifold.
        point_b : array-like
            Point on the manifold.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        metric = self.metric(*metric_args)
        sd_a_b = metric.squared_dist(gs.array(point_a), gs.array(point_b))
        sd_b_a = metric.squared_dist(gs.array(point_b), gs.array(point_a))
        self.assertAllClose(sd_a_b, sd_b_a, rtol=rtol, atol=atol)

    def parallel_transport_ivp_is_isometry(
        self,
        metric_args,
        space,
        tangent_vec,
        base_point,
        direction,
        is_tangent_atol,
        rtol,
        atol,
    ):
        """Check that parallel transport is an isometry.

        This is for parallel transport defined by initial value problem (ivp).

        Parameters
        ----------
        metric_args : tuple
            Arguments to pass to constructor of the metric.
        space : Manifold
            Manifold where metric is defined.
        tangent_vec : array-like
            Tangent vector at base point, to be transported.
        base_point : array-like
            Point on manifold.
        direction : array-like
            Tangent vector at base point, along which to transport.
        is_tangent_atol: float
            Asbolute tolerance for the is_tangent function.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        metric = self.metric(*metric_args)

        end_point = metric.exp(direction, base_point)

        transported = metric.parallel_transport(tangent_vec, base_point, direction)
        result = _is_isometry(
            metric,
            space,
            tangent_vec,
            transported,
            end_point,
            is_tangent_atol,
            rtol,
            atol,
        )
        expected = gs.array(len(result) * [True])
        self.assertAllClose(result, expected)

    def parallel_transport_bvp_is_isometry(
        self,
        metric_args,
        space,
        tangent_vec,
        base_point,
        end_point,
        is_tangent_atol,
        rtol,
        atol,
    ):
        """Check that parallel transport is an isometry.

        This is for parallel transport defined by boundary value problem (ivp).

        Parameters
        ----------
        metric_args : tuple
            Arguments to pass to constructor of the metric.
        space : Manifold
            Manifold where metric is defined.
        tangent_vec : array-like
            Tangent vector at base point, to be transported.
        base_point : array-like
            Point on manifold.
        end_point : array-like
            Point on manifold.
        is_tangent_atol: float
            Asbolute tolerance for the is_tangent function.
        rtol : float
            Relative tolerance to test this property.
        atol : float
            Absolute tolerance to test this property.
        """
        metric = self.metric(*metric_args)

        transported = metric.parallel_transport(
            tangent_vec, base_point, end_point=end_point
        )
        result = _is_isometry(
            metric,
            space,
            tangent_vec,
            transported,
            end_point,
            is_tangent_atol,
            rtol,
            atol,
        )
        expected = gs.array(len(result) * [True])
        self.assertAllClose(result, expected)
